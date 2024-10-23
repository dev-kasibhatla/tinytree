import json
import sys
import os
import shutil


def validate_config():
    config_file = 'config.json'
    if not os.path.exists(config_file):
        print(f"Config file not found: {config_file}")
        sys.exit(1)

    required_root_keys = {'public_folder': str, 'default_css': str, 'pages': dict}
    required_page_keys = {'title': str, 'subtitle': str, 'seo_keywords': list, 'links': dict}
    required_link_keys = {'title': str, 'subtitle': str, 'url': str}

    try:
        with open(config_file) as config:
            config_data = json.load(config)

        for key, value in required_root_keys.items():
            if key not in config_data or not isinstance(config_data[key], value):
                print(f"Missing or invalid type for key: '{key}'")
                sys.exit(1)

        for page, page_data in config_data['pages'].items():
            for key, value in required_page_keys.items():
                if key not in page_data or not isinstance(page_data[key], value):
                    print(f"Missing or invalid type for key '{key}' in page '{page}'")
                    sys.exit(1)

                for link, link_data in page_data['links'].items():
                    for key, value in required_link_keys.items():
                        if key not in link_data or not isinstance(link_data[key], value):
                            print(f"Missing or invalid type for key '{key}' in link '{link}' for page '{page}'")
                            sys.exit(1)

    except json.JSONDecodeError as e:
        print(f"Invalid JSON format in '{config_file}': {e}")
        sys.exit(1)

    print("Config file is valid.")
    return config_data


def create_dir_if_not_exists(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def generate_dir_structure(config):
    """
    Generates the project directory structure.

    Args:
        config (dict): Contains 'public_folder', 'default_css', and 'pages'.

    Steps:
        1. Remove and recreate 'public_folder'.
        2. Copy 'default_css' to 'public_folder'.
        3. For each page in 'pages', create a directory and copy custom CSS if specified.
    """
    print("Generating directory structure")
    if os.path.exists(config['public_folder']):
        shutil.rmtree(config['public_folder'])

    create_dir_if_not_exists(config['public_folder'])
    if not os.path.exists(config['default_css']):
        print(f"Default CSS file not found: {config['default_css']}")
        sys.exit(1)
    shutil.copy(config['default_css'], os.path.join(config['public_folder'], os.path.basename(config['default_css'])))

    for page, page_data in config['pages'].items():
        page_dir = os.path.join(config['public_folder'], page)
        create_dir_if_not_exists(page_dir)
        if 'css' in page_data:
            if not os.path.exists(page_data['css']):
                print(f"Custom CSS file not found: {page_data['css']}")
                sys.exit(1)
            dst_css_file = os.path.join(config['public_folder'], os.path.basename(page_data['css']))
            if not os.path.exists(dst_css_file):
                shutil.copy(page_data['css'], dst_css_file)

    print("Directory structure generated.")


def get_boilerplate_content():
    with open('templates/boiler-main.html') as boiler_main, open('templates/boiler-link.html') as boiler_link:
        return boiler_main.read(), boiler_link.read()


def get_scripts_content():
    with open('templates/scripts.js', 'r') as scripts_file:
        scripts_content = scripts_file.read()

    return scripts_content


def generate_files(config):
    print("Generating files")
    boiler_main, boiler_link = get_boilerplate_content()
    scripts_content = get_scripts_content()

    for page, page_data in config['pages'].items():
        page_file = os.path.join(config['public_folder'], page, 'index.html')

        # Prepare file content
        main_content = boiler_main.replace('--title', page_data['title']) \
            .replace('--subtitle', page_data['subtitle']) \
            .replace('--seo_keywords', ', '.join(page_data['seo_keywords'])) \
            .replace('--css-location', f'/{os.path.basename(page_data.get("css", config["default_css"]))}')

        links_content = ''.join(
            boiler_link.replace('--link-title', link_data['title'])
            .replace('--link-subtitle', link_data['subtitle'])
            .replace('--link-location', link_data['url'])
            for link, link_data in page_data['links'].items()
        )

        main_content = main_content.replace('--links', links_content).replace('--scripts', scripts_content)

        with open(page_file, 'w') as f:
            f.write(main_content)

    print("Files generated.")


def main():
    config = validate_config()
    generate_dir_structure(config)
    generate_files(config)


if __name__ == '__main__':
    main()
