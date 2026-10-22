# Deleted-account pool quarantine — 1.1.21

A native account deletion can remove passwd and Webuzo userdata before its PHP-FPM pool text disappears. The previous parser raised KeyError and could fail the whole coordinator, interrupting other accounts. The new parser skips ONLY that dead pool when its username is syntactically valid, userdata is absent, group matches the username and the listener is the expected native per-account socket. It never serves the deleted pool or falls back to another user/shared PHP. Existing nonhosting/privileged accounts, partial deletion with remaining userdata, nonstandard listeners and wrong groups still fail validation.

## Deployment and exact source placement

A full replacement source is shipped in `core/webuzo-isolation.py` inside the plugin. Repository copies are `uniselv-resource-manager/core/webuzo-isolation.py` and `uniselv-resource-manager/plugin/core/webuzo-isolation.py`.

Live copies: `/usr/local/sbin/webuzo-isolation.py`, `/usr/local/uniselv-resman/core/webuzo-isolation.py`, `/usr/local/webuzo/plugins/uniselv-resman/core/webuzo-isolation.py`. Preserve root ownership and existing modes. The automated maintenance performs atomic replacement after syntax checking and archives previous source/ownership metadata privately. No native per-user PHP-FPM overrides are created.

For review/manual backport, inside `parse_pools()` REPLACE the one existing line `account=pwd.getpwnam(user)` (eight leading spaces). Do not insert a second account lookup or duplicate exception handler.

AFTER this existing line:

```python
        if not re.fullmatch(r'[a-z_][a-z0-9_-]{0,31}',user):raise ValueError('Invalid pool username')
```

BEFORE this existing line:

```python
        if account.pw_uid<1000 or not (pathlib.Path('/var/webuzo/users')/user).exists():raise ValueError('Not an eligible Webuzo account: '+user)
```

REPLACEMENT CODE — copy this block only:

```python
        try:
            account=pwd.getpwnam(user)
        except KeyError:
            # Native deletion can remove passwd/userdata before regenerating FPM.
            # Quarantine this dead, standard-shaped pool, never route it through
            # another UID or stop unrelated accounts while the vendor catches up.
            expected=str(prefix/'var'/('fpm-'+user+'.sock'))
            if (pathlib.Path('/var/webuzo/users')/user).exists() or field('group')!=user or field('listen')!=expected:
                raise ValueError('Missing account with nonstandard native pool: '+user)
            print('Ignoring native pool pending deleted-account regeneration: '+version+' '+user,file=sys.stderr,flush=True)
            continue
```

Illustrative AFTER-edit context — DO NOT paste this second example:

```python
        user=field('user')
        if not re.fullmatch(r'[a-z_][a-z0-9_-]{0,31}',user):raise ValueError('Invalid pool username')
        try:
            account=pwd.getpwnam(user)
        except KeyError:
            # Native deletion can remove passwd/userdata before regenerating FPM.
            # Quarantine this dead, standard-shaped pool, never route it through
            # another UID or stop unrelated accounts while the vendor catches up.
            expected=str(prefix/'var'/('fpm-'+user+'.sock'))
            if (pathlib.Path('/var/webuzo/users')/user).exists() or field('group')!=user or field('listen')!=expected:
                raise ValueError('Missing account with nonstandard native pool: '+user)
            print('Ignoring native pool pending deleted-account regeneration: '+version+' '+user,file=sys.stderr,flush=True)
            continue
        if account.pw_uid<1000 or not (pathlib.Path('/var/webuzo/users')/user).exists():raise ValueError('Not an eligible Webuzo account: '+user)
        original=str(prefix/'var'/('fpm-'+user+'.sock'))
```

Save the complete file, run Python syntax compilation and the included dated regression evidence, verify coordinator/native service bridges and actual HTTP containment. Do not blindly restart every active customer pool just to reload a file. A failed coordinator may be started after its source/metadata are repaired; active supervisors need controlled reload/restart handling. Back up and update owned-source digest metadata together; preserve the original restoration history. Existing package-version fields are replaced by the new full `info.json` and plugin PHP header, never duplicated.

## Verification and limits

Seven checks cover a live pool, a fully deleted standard pool alongside a live pool, wrong group, nonstandard listener, remaining userdata, privileged accounts and duplicate live pools. Actual live deletion/reconciliation evidence is recorded separately. Native administrative operations may explicitly stop/start PHP; quarantine does not promise zero downtime during those operations. A direct host view of an empty native FPM config is not the effective private health config; validate the running health master's mount namespace.

Current-host quota recovery is an OS prerequisite repair: matching official kernel modules were missing; loading quota_v2 and enabling native user quotas repaired block/inode enforcement. It does not change hosting resource-plan values or automatically install packages on every kernel update. Do not enable host swap without separate account swap-boundary tests.

Use actual `--rebuild_vhost` regeneration when validating routing. An exploratory native `--rebuild-user` removed the disposable probe; do not use that reset/rebuild operation on real customer data as a routine recovery command or count it as data-preserving regeneration.

This documentation is a new file from its first heading through this final paragraph. No content is to be inserted into a native panel file. Evidence and remaining gates are in `server-configuration-validation-20261021.json`; all prior WordPress-capacity and lifecycle limitations remain applicable until explicitly retested.
