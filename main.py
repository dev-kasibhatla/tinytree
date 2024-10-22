import json
import sys
import os

def extract_args():
    return {}

def validate_config():
    config_file = 'config.json'
    if not os.path.exists(config_file):
        print(f"Config file not found: {config_file}")
        sys.exit(1)

    required_root_keys = {
        'public_folder': str,
        'default_css': str,
        'pages': dict
    }

    required_page_keys = {
        'title': str,
        'subtitle': str,
        'seo_keywords': list,
        # 'css': str,
        'links': dict
    }

    required_link_keys = {
        'title': str,
        'subtitle': str,
        'url': str
    }

    try:
        with open(config_file, 'r') as config:
            config_data = json.load(config)

        for key, value in required_root_keys.items():
            if key not in config_data:
                print(f"Missing required key: '{key}'")
                sys.exit(1)
            if not isinstance(config_data[key], value):
                print(f"Invalid type for key '{key}': must be {value.__name__}")
                sys.exit(1)

        for page, page_data in config_data['pages'].items():
            for key, value in required_page_keys.items():
                if key not in page_data:
                    print(f"Missing required key '{key}' in page '{page}'")
                    sys.exit(1)
                if not isinstance(page_data[key], value):
                    print(f"Invalid type for key '{key}' in page '{page}': must be {value.__name__}")
                    sys.exit(1)

                for link, link_data in page_data['links'].items():
                    for key, value in required_link_keys.items():
                        if key not in link_data:
                            print(f"Missing required key '{key}' in link '{link}' for page '{page}'")
                            sys.exit(1)
                        if not isinstance(link_data[key], value):
                            print(f"Invalid type for key '{key}' in link '{link}' for page '{page}': must be {value.__name__}")


    except json.JSONDecodeError as e:
        print(f"Invalid JSON format in '{config_file}': {e}")
        sys.exit(1)

    print("Config file is valid.")
    return config_data


def create_dir_if_not_exists(dir_path):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

def generate_dir_structure(config):
    create_dir_if_not_exists(config['public_folder'])
    for page, page_data in config['pages'].items():
        page_dir = os.path.join(config['public_folder'], page)
        create_dir_if_not_exists(page_dir)

    print("Directory structure generated.")

def get_boilerplate_content():
    with open('boiler-main.html', 'r') as boiler_main:
        boiler_main_content = boiler_main.read()

    with open('boiler-link.html', 'r') as boiler_link:
        boiler_link_content = boiler_link.read()

    return boiler_main_content, boiler_link_content

def get_scripts_content():
    with open('scripts.js', 'r') as scripts_file:
        scripts_content = scripts_file.read()

    return scripts_content

def generate_files(config):
    boiler_main, boiler_link = get_boilerplate_content()
    scripts_content = get_scripts_content()

    for page, page_data in config['pages'].items():
        page_dir = os.path.join(config['public_folder'], page)
        page_file = os.path.join(page_dir, 'index.html')

        # prepare file content
        main_content = boiler_main.replace('--title', page_data['title'])
        main_content = main_content.replace('--subtitle', page_data['subtitle'])
        main_content = main_content.replace('--seo_keywords', ', '.join(page_data['seo_keywords']))
        css_location = config['default_css']
        if 'css' in page_data:
            css_location = page_data['css']
        main_content = main_content.replace('--css-location', css_location)

        links_content = ''
        for link, link_data in page_data['links'].items():
            link_content = boiler_link.replace('--link-title', link_data['title'])
            link_content = link_content.replace('--link-subtitle', link_data['subtitle'])
            link_content = link_content.replace('--link-location', link_data['url'])
            links_content += link_content

        main_content = main_content.replace('--links', links_content)
        main_content = main_content.replace('--scripts', scripts_content)

        with open(page_file, 'w') as page_file:
            page_file.write(main_content)

    print("Files generated.")


def main():
    arg_dict = extract_args()
    config = validate_config()
    generate_dir_structure(config)
    generate_files(config)

if __name__ == '__main__':
    main()
