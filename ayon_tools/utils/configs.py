import os
import json
from pathlib import Path

import requests
import ayon_api
from .auth import auth


def get_studio_presets_names():
    presets = ayon_api.get_project_anatomy_presets()
    return [x['name'] for x in presets]


def get_studio_preset(preset_name: str):
    return ayon_api.get_project_anatomy_preset(preset_name)


def upload_studio_preset(preset: str, preset_name: str):
    url = f'{auth.SERVER_URL}/api/anatomy/presets/{preset_name}'
    if isinstance(preset, (str, Path)):
        with open(preset) as f:
            preset = json.load(f)
    resp = requests.put(url, json=preset, headers=auth.HEADERS)
    resp.raise_for_status()


def get_project_anatomy(project_name: str):
    url = f'{auth.SERVER_URL}/api/projects/{project_name}/anatomy'
    return requests.get(url=url, headers=auth.HEADERS).json()


def update_project_anatomy(project_name: str, anatomy: str or dict):
    url = f'{auth.SERVER_URL}/api/projects/{project_name}/anatomy'
    if isinstance(anatomy, str):
        with open(anatomy) as f:
            anatomy = json.load(f)
    assert isinstance(anatomy, dict)
    resp = requests.post(url, json=anatomy, headers=auth.HEADERS)
    resp.raise_for_status()


def get_bundle(bundle_name: str = None):
    for bundle in get_bundles():
        if bundle['name'] == bundle_name:
            return bundle


def get_production_bundle():
    for b in get_bundles(archived=False):
        if b['isProduction']:
            return b


def get_bundles(archived=False):
    url = f'{auth.SERVER_URL}/api/bundles?archived={str(archived).lower()}'
    return requests.get(url=url, headers=auth.HEADERS).json()['bundles']


def get_dep_packages():
    # url = f'{auth.SERVER_URL}/api/desktop/dependency_packages'
    url = f'{auth.SERVER_URL}/api/desktop/dependencyPackages'
    data = requests.get(url=url, headers=auth.HEADERS).json()
    return data['packages']


def create_bundle(name, addons: dict, production=False, stage=False, installer_version=None):
    dep_packages = get_dep_packages()
    installer = installer_version or max([x['installerVersion'] for x in dep_packages])
    bundle_data = {
        # addons: {"core": "0.0.1", ...}
        "addons": addons,
        "installerVersion": installer,
        "name": name,
        "dependencyPackages": {x['platform']: x['filename'] for x in dep_packages},
        "isArchived": False,
        "isStaging": stage,
        "isProduction": production,
        "isDev": False,
        "addonDevelopment": {}
    }
    resp = requests.post(f'{auth.SERVER_URL}/api/bundles', json=bundle_data, headers=auth.HEADERS)
    resp.raise_for_status()


def get_addon_settings(addon_name: str, version: str):
    url = f'{auth.SERVER_URL}/api/addons/{addon_name}/{version}/settings?variant=production'
    return requests.get(url=url, headers=auth.HEADERS).json()


def set_addon_settings(addon_name: str, version: str, settings: dict):
    url = f'{auth.SERVER_URL}/api/addons/{addon_name}/{version}/settings?variant=production'
    requests.post(url=url, json=settings, headers=auth.HEADERS).raise_for_status()


def get_project_addon_settings(project_name: str, addon_name: str, version: str):
    url = f'{auth.SERVER_URL}/api/addons/{addon_name}/{version}/settings/{project_name}?variant=production'
    return requests.get(url=url, headers=auth.HEADERS).json()


def set_project_addon_settings(project_name: str, addon_name: str, version: str, settings: dict):
    url = f'{auth.SERVER_URL}/api/addons/{addon_name}/{version}/settings/{project_name}?variant=production'
    requests.post(url=url, json=settings, headers=auth.HEADERS).raise_for_status()


def get_project_addons_settings(project_name: str, bundle_name: str = None, skip_addons: list = None):
    if bundle_name:
        bundle = get_bundle(bundle_name)
    else:
        bundle = get_production_bundle()
    print('GET FROM BUNDLE:', bundle['name'])
    addons = {}
    for addon, version in bundle['addons'].items():
        if skip_addons and addon in skip_addons:
            continue
        addons[addon] = {
            'version': version,
            'settings': get_project_addon_settings(project_name, addon_name=addon, version=version)
        }
    return addons


def set_project_addons_settings(project_name: str, addons: dict, skip_addons: list = None):
    bundle = get_production_bundle()
    print('SET TO BUNDLE:', bundle['name'])
    errors = []
    for addon, version in bundle['addons'].items():
        if skip_addons and addon in skip_addons:
            print('Skip', addon)
            continue
        if addon not in addons:
            # errors.append(f'Addon "{addon}" is not in bundle {bundle["name"]}')
            print(f'Addon "{addon}" is not in bundle {bundle["name"]}')
            continue
        if addons[addon]['version'] != version:
            errors.append(f'Addon "{addon}" version is not equal to bundle version: {addons[addon]["version"]} > {version}')
            continue
    if errors:
        for error in errors:
            print(error)
        raise Exception('Some errors occurred')
    for addon, data in addons.items():
        version = data['version']
        settings = data['settings']
        try:
            set_project_addon_settings(project_name, addon, version, settings)
        except requests.exceptions.HTTPError:
            print(f'Error setting addon "{addon}" settings')


def get_project_all_settings(project_name: str, bundle_name: str = None, skip_addons: list = None):
    return {
        'anatomy': get_project_anatomy(project_name),
        'addons': get_project_addons_settings(project_name, bundle_name, skip_addons),
    }


def get_attributes():
    url = f'{auth.SERVER_URL}/api/attributes'
    return requests.get(url=url, headers=auth.HEADERS).json()


def set_attributes(attributes: dict):
    url = f'{auth.SERVER_URL}/api/attributes'
    requests.put(url=url, json=attributes, headers=auth.HEADERS).raise_for_status()


# def get_all_project_settings(project_name):
#     bundle = get_production_bundle()
#     return dict(
#         anatomy=get_project_anatomy(project_name),
#         # attributes=get_attributes(),
#         bundle=bundle,
#         addon_settings={addon_name: get_project_addon_settings(project_name, addon_name, version)
#                         for addon_name, version in bundle['addons'].items()},
#     )


# def set_all_project_settings(project_name, settings):
#     update_project_anatomy(project_name, settings['anatomy'])
#     for addon_name, addon_conf in settings['addon_settings'].items():
#         addon_version = settings['bundle']['addons'].get(addon_name)
#         if addon_version:
#             try:
#                 set_project_addon_settings(project_name, addon_name, addon_version, addon_conf)
#             except Exception as e:
#                 print(addon_name, e)


def clone_project(from_url: str, from_api_key: str,
                  to_url: str, to_api_key: str,
                  from_project_name: str,
                  to_project_name: str = None):
    # get data
    to_project_name = to_project_name or from_project_name
    from_project = ayon_api.get_project(from_project_name)
    if not from_project:
        raise NameError('Source Project not found')
    auth.set_credentials(from_url, from_api_key)
    src_project_anatomy = get_project_anatomy(from_project_name)
    # set data
    auth.set_credentials(to_url, to_api_key)
    trg_project = ayon_api.get_project(to_project_name)
    if not trg_project:
        from ayon_api.utils import slugify_string
        ayon_api.create_project(to_project_name, slugify_string(to_project_name))
    update_project_anatomy(to_project_name, src_project_anatomy)
    # set_all_project_settings(to_project_name, src_project_conf)


def clone_addon_settings(from_url: str, from_api_key: str,
                         to_url: str, to_api_key: str,
                         from_project_name: str,
                         to_project_name: str = None,
                         bundle_name: str = None,
                         skip_addons: list = None):
    to_project_name = to_project_name or from_project_name
    # get
    auth.set_credentials(from_url, from_api_key)
    settings = get_project_addons_settings(from_project_name, bundle_name, skip_addons)
    # set
    auth.set_credentials(to_url, to_api_key)
    set_project_addons_settings(to_project_name, settings, skip_addons)


def clone_studio_anatomy_preset(from_url: str, from_api_key: str,
                                to_url: str, to_api_key: str,
                                from_preset_name: str, to_preset_name: str = None):
    to_preset_name = to_preset_name or from_preset_name
    auth.set_credentials(from_url, from_api_key)
    src_preset = get_studio_preset(from_preset_name)
    auth.set_credentials(to_url, to_api_key)
    upload_studio_preset(src_preset, to_preset_name)


def clone_attributes(from_url: str, from_api_key: str,
                     to_url: str, to_api_key: str):
    auth.set_credentials(from_url, from_api_key)
    attrs = get_attributes()
    auth.set_credentials(to_url, to_api_key)
    set_attributes(attrs)


def clone_bundle(from_url: str, from_api_key: str,
                 to_url: str, to_api_key: str,
                 from_bundle_name: str = None,
                 to_bundle_name: str = None):
    # get current bundle
    # get addon list
    # check addons on new server
    # create new bundle
    # copy addon settings
    pass


def dump_server_settings(url: str, api_key: str, filename: str):
    auth.set_credentials(url, api_key)
    # addon settings
    bundle = get_production_bundle()
    addon_settings = {}
    for addon, version in bundle['addons'].items():
        settings = get_addon_settings(addon, version)
        addon_settings[addon] = settings
    # anatomy
    preset_names = get_studio_presets_names()
    presets = {}
    for name in preset_names:
        presets[name] = get_studio_preset(name)
    # attributes
    attribs = get_attributes()
    data = dict(
        bundle=bundle, studio_presets=presets, attributes=attribs, addons=addon_settings
    )
    with open(filename, 'w') as f:
        json.dump(data, f, indent=2)


def restore_server_settings(url: str, api_key: str, filename: str):
    auth.set_credentials(url, api_key)
    with open(filename, 'r') as f:
        data = json.load(f)
    # bundle
    bundle = data['bundle']
    create_bundle(bundle['name'], addons=bundle['addons'], production=True)
    # studio presets
    for name, preset in data['studio_presets'].items():
        upload_studio_preset(preset, name)
    # attributes
    set_attributes(data['attributes'])
    # addons
    for addon, settings in data['addons'].items():

        try:
            set_addon_settings(addon, bundle['addons'][addon], settings)
        except Exception as e:
            print(f"Restore {addon} {bundle['addons'][addon]} FAILED: {e}")