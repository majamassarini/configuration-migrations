from yaml import safe_load


commit_msg = """Fix configuration for Packit 1.0.0

This commit fixes the configuration for the forthcoming Packit 1.0.0.
See [our blog post](https://packit.dev/posts/packit_1_0_0_action_required) for more details.
  - Job type `build` has been changed to `copr_build`.
  - Job type `production_build` has been changed to `upstream_koji_build`.
  - Key `upstream_project_name` has been changed to `upstream_package_name`.
  - Key `synced_files` has been changed to `files_to_sync`.

Please review and merge me before January 2025 otherwise packit-service jobs will fail because of an invalid configuration.
"""


def get_config_migration_keys(packit_config_dict: str):
    jobs = packit_config_dict.get("jobs", [])
    build_jobs = [
        job
        for job in jobs
        if job.get("job") == "build"
    ]
    production_build_jobs = [
        job
        for job in jobs
        if job.get("job") == "production_build"
    ]
    upstream_project_name = packit_config_dict.get("upstream_project_name")
    synced_files = packit_config_dict.get("synced_files")
    files_to_sync = packit_config_dict.get("files_to_sync")

    return (
        build_jobs,
        production_build_jobs,
        upstream_project_name,
        synced_files,
        files_to_sync
    )

def is_package_config_affected(package_config: str) -> bool:
    packit_config_dict = safe_load(package_config)

    (build_jobs, production_build_jobs, upstream_project_name, 
     synced_files, _) = get_config_migration_keys(packit_config_dict)

    return (
        build_jobs
        or production_build_jobs
        or upstream_project_name
        or synced_files
    )


def migrate_package_config(package_config: str) -> str:
    packit_config_dict = safe_load(package_config)

    (build_jobs, production_build_jobs, upstream_project_name, 
     synced_files, files_to_sync) = get_config_migration_keys(packit_config_dict)

    new_package_config = package_config
    if build_jobs:
        new_package_config = new_package_config.replace("job: build", "job: copr_build")
    if production_build_jobs:
        new_package_config = new_package_config.replace("job: production_build", "job: upstream_koji_build")
    if upstream_project_name:
        new_package_config = new_package_config.replace("upstream_project_name", "upstream_package_name")
    if synced_files and not files_to_sync:
        new_package_config = new_package_config.replace("synced_files", "files_to_sync")

    return new_package_config
