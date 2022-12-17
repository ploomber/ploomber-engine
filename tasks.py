from invoke import task


@task(aliases=["s"])
def setup(c, version=None, doc=False):
    """
    Setup dev environment, requires conda
    """
    version = version or "3.10"
    suffix = "" if version == "3.10" else version.replace(".", "")

    if doc:
        suffix += "-doc"

    env_name = f"ploomber-engine{suffix}"

    c.run(f"conda create --name {env_name} python={version} --yes")
    c.run(
        'eval "$(conda shell.bash hook)" '
        f"&& conda activate {env_name} "
        "&& pip install --editable .[dev]"
    )

    if doc:
        c.run(
            'eval "$(conda shell.bash hook)" '
            f"&& conda activate {env_name} "
            "&& pip install -r doc/requirements.txt"
        )

    print(f"Done! Activate your environment with:\nconda activate {env_name}")


@task(aliases=["d"])
def doc(c):
    """Build documentation"""
    c.run("jupyter-book build doc/")


@task(aliases=["v"])
def version(c):
    """Release a new version"""
    from pkgmt import versioneer

    versioneer.version(project_root=".", tag=True)


@task(aliases=["r"])
def release(c, tag, production=True):
    """Upload to PyPI"""
    from pkgmt import versioneer

    versioneer.upload(tag, production=production)
