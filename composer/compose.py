import os
import sys
from glob import glob
# from parse import parse # not using anymore (keeping for temp-ref
import json
import re
import yaml
import argparse
from typing import List, Tuple, Dict, Union, Any, Optional, Callable, NewType

PAT = re.compile(".*(?P<command_id>\d{3})-(?:the-)?(?P<slug>.*)-command.md")
PREFIX = '<strong>'
SUFFIX = '</strong>'
NAV_PATTERN = "<code>{command_id}:&nbsp;{slug}</code>"

SlugmapType = NewType("SlugmapType", Dict[str, Dict[str, str]])
CommandNavsType = NewType("CommandNavsType", List[Dict[str, str]])
NavsDataType = NewType("NavsDataType", Dict[str, List[Union[str, Dict[str, Union[str, List[Union[str, Dict]]]]]]])

# docs_dir = "../docs"
# files = glob(f'{docs_dir}/ebook/en/content/*.md')
# files.sort()
#print(files)

def get_navs_skeleton(
        files: List[str], 
        docs_dir: str='../docs', 
        command_filename_endswith: str="command.md",
        **kwargs
    ) -> Tuple[SlugmapType, CommandNavsType]:
    """Returns nav skeleton in the form of a list (`command_navs`) and a dict (`slugmap`)."""

    command_navs = []
    slugmap = dict()

    for file in files:
        if file.endswith(command_filename_endswith):
            #slug = PAT.findall(file)[0]
            match = PAT.match(file).groupdict()
            slug = match.get('slug')
            command_id = match.get('command_id')
            slug_label = slug
            parts = slug.split('-')
            if isinstance(parts, list):
                parts = [part.title() if 'introduction' == part else part for part in parts]
                slug = f'{PREFIX}' + f'{SUFFIX}&nbsp;and&nbsp;{PREFIX}'.join(parts) + f'{SUFFIX}'
            path = file.replace(f"{docs_dir}/", "")
            slugmap.update({slug_label: {
                "command_id": command_id,
                "slug": slug,
                "path": path,
                },
            })

            command_navs.append({NAV_PATTERN.format(slug=slug, command_id=command_id): path})

    return slugmap, command_navs

def create_navs_data(command_navs: CommandNavsType, **kwargs) -> NavsDataType:

    navs_data = {
        "nav": [
            {"<p><i class='fas fa-home'>&nbsp;</i> Home</p>": "index.md"},
            {
                "<p><i class='fas fa-terminal'>&nbsp;</i>Commands</p>": command_navs +
                    [{"Wrap Up": "ebook/en/content/999-wrap-up.md"}],
            },
            {
                "<p><i class='fas fa-download'>&nbsp;</i>Download</p>": [
                    {"Download eBook": "download.md"},
                ],
            },
            {
                "<p><i class='fas fa-info-circle'>&nbsp;</i>About</p>": [
                    {"Info": "about/index.md"},
                    {"License": "about/license.md"},
                ],
            },
        ],
    }

    return navs_data

def generate_nav(
        docs_dir: str='../docs', 
        dry_run: bool=False, 
        create_slugmap: bool=True, 
        ebook_pattern: str="ebook/en/content/*.md",
        command_filename_endswith: str="command.md",
        slugmap_filename: str="slugmap.json",
        command_navs_filename: str="command_navs.yml",
        **kwargs
    ):
    """Generates nav structure from ebook content-files."""

    # Acquire target file names
    files = glob(f'{docs_dir}/{ebook_pattern}')
    files.sort()
    
    #print(len(files))

    # Generate nav skeleton for commands
    # :: for each "*-command.md" file:
    # - slugmap: a key-value mapping of slug used.
    # - command_navs: a list of key-value mapping of navs.
    slugmap, command_navs = get_navs_skeleton(
        files, 
        docs_dir=docs_dir, 
        command_filename_endswith=command_filename_endswith,
        **kwargs
    )

    # Write slugmap to a persistent file: 'slugmap.json'
    if create_slugmap:
        with open(f'{docs_dir}/{slugmap_filename}', 'w') as f:
            f.write(json.dumps(slugmap, indent=2))

    # Generate navigation structure for mkdocs.yml
    navs_data = create_navs_data(command_navs, **kwargs)

    # Display/Write to file the navs-struture
    if dry_run:
        # Display
        yaml.dump(navs_data, None,
            default_flow_style=False,
            default_style='"',
            indent=2,
        )
    else:
        # Write to file: 'command_navs.yml'
        with open(f'{docs_dir}/{command_navs_filename}', 'w') as f:
            yaml.dump(navs_data, f,
                default_flow_style=False,
                default_style='"',
                indent=2,
            )

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description='Dynamically generate navigation for documentation.')
    generate_nav()
