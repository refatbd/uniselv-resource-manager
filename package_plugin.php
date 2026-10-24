<?php
/** Native ZIP builder. Source text uses LF; Linux package paths and modes are verified. */
function buildReleaseZip(string $root, string $target, string $prefix): array {
    $root = realpath($root);
    if (!$root || !is_dir($root)) throw new RuntimeException('Source directory missing');
    $zip = new ZipArchive();
    if ($zip->open($target, ZipArchive::CREATE | ZipArchive::OVERWRITE) !== true) throw new RuntimeException('Cannot open ZIP');
    $expected = [];
    $putDirectory = function(string $name) use ($zip) {
        $name = rtrim(str_replace('\\', '/', $name), '/') . '/';
        $zip->addEmptyDir($name);
        if (!$zip->setExternalAttributesName($name, ZipArchive::OPSYS_UNIX, 0040755 << 16)) throw new RuntimeException('Directory mode failed');
    };
    if ($prefix !== '') $putDirectory($prefix);
    $it = new RecursiveIteratorIterator(new RecursiveDirectoryIterator($root, FilesystemIterator::SKIP_DOTS), RecursiveIteratorIterator::SELF_FIRST);
    $entries = [];
    foreach ($it as $file) {
        $rel = str_replace('\\', '/', substr($file->getPathname(), strlen($root) + 1));
        if (preg_match('~(^|/)(\.git|__pycache__|node_modules|\.pytest_cache)(/|$)~', $rel) || preg_match('~\.(pyc|zip|log|bak)$~', $rel)) continue;
        if ($file->isLink()) throw new RuntimeException('Refusing symlink in package: '.$rel);
        $entries[$rel] = $file;
    }
    ksort($entries);
    foreach ($entries as $rel=>$file) {
        $name = ($prefix !== '' ? trim($prefix,'/').'/' : '').$rel;
        if ($file->isDir()) { $putDirectory($name); continue; }
        $bytes = file_get_contents($file->getPathname());
        if (preg_match('~\.(py|php|sh|conf|json|md|txt|css|js|svg|html|xml|ya?ml)$~i', $rel)) $bytes = str_replace("\r\n", "\n", $bytes);
        if (!$zip->addFromString($name, $bytes) || !$zip->setExternalAttributesName($name, ZipArchive::OPSYS_UNIX, 0100644 << 16)) throw new RuntimeException('File write/mode failed: '.$rel);
        $expected[$name] = hash('sha256', $bytes);
    }
    if (!$zip->close()) throw new RuntimeException('ZIP closure failed');
    if ($zip->open($target, ZipArchive::CHECKCONS) !== true) throw new RuntimeException('ZIP integrity failed');
    for ($i=0;$i<$zip->numFiles;$i++) {
        $name=$zip->getNameIndex($i);
        if (str_contains($name,'\\') || str_starts_with($name,'/') || str_contains($name,'../')) throw new RuntimeException('Unsafe ZIP path');
        $zip->getExternalAttributesIndex($i,$opsys,$attrs);
        $directory=str_ends_with($name,'/');
        if ($opsys !== ZipArchive::OPSYS_UNIX || (($attrs>>16)&0777)!==($directory?0755:0644)) throw new RuntimeException('ZIP permission mismatch');
        if (!$directory && (!isset($expected[$name]) || hash('sha256',$zip->getFromIndex($i))!==$expected[$name])) throw new RuntimeException('Source closure mismatch');
    }
    $count=$zip->numFiles;$zip->close();
    $sha=hash_file('sha256',$target);file_put_contents($target.'.sha256',$sha.'  '.basename($target)."\n");
    return ['path'=>$target,'sha256'=>$sha,'entries'=>$count];
}
if (realpath($_SERVER['SCRIPT_FILENAME'] ?? '') === __FILE__) {
    $root=__DIR__.'/plugin';$info=json_decode(file_get_contents($root.'/info.json'),true,512,JSON_THROW_ON_ERROR);$v=$info['version'];
    if (!preg_match('/^Version:\s*'.preg_quote($v,'/').'\s*$/m',file_get_contents($root.'/uniselv-resman.php'))) throw new RuntimeException('Version mismatch');
    if (!str_contains(file_get_contents($root.'/uniselv-resman.php'),$v.'r1')) throw new RuntimeException('Asset release key mismatch');
    $result=buildReleaseZip($root,__DIR__.'/uniselv-resman-'.$v.'.zip','uniselv-resman');
    copy($result['path'],__DIR__.'/uniselv-resman.zip');file_put_contents(__DIR__.'/uniselv-resman.zip.sha256',$result['sha256'].'  uniselv-resman.zip'."\n");
    echo json_encode($result,JSON_PRETTY_PRINT)."\n";
}
