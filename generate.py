#!/usr/bin/env python3

import logging
import os
import subprocess
import time

from re import search
from lxml import etree
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, wait, ALL_COMPLETED

print_maps_path = os.path.abspath('./bin/printmaps')


class MapDefinition:
    def __init__(self, path):
        if not os.path.exists(path) or not os.path.isdir(path):
            raise "path %s is not a directory" % path
        
        self.path = os.path.abspath(path)
        self.name = os.path.basename(path)
    
    def __execute_command(self, action: str) -> (int, str):
        logging.info(f'{self.name}: call \'{action}\'')
        
        result = subprocess.run([print_maps_path, action], capture_output=True, text=True, cwd=self.path)
        output: str = result.stdout

        return result.returncode, output

    def __renew_map_id(self):
        filename = "map.id"
        abs_filename = os.path.join(self.path, filename)
                
        if os.path.exists(abs_filename):
            os.remove(abs_filename)
        
        logging.info(f'{self.name}: create {filename}')
        
        return_code, _ = self.__execute_command('create')

        if return_code != 0:
            logging.error(f'{self.name}: unable to create {filename}')

    def __try_to_update(self):
        returned_output = self.__execute_command('update')
        
        logging.info(f'{self.name}: result: {returned_output}')

    def __update_legend(self):
        legend_file = 'legend.svg'
        legend_file_as_path = 'legend-path.svg'
        
        abs_legend_file = os.path.join(self.path, legend_file)
        abs_legend_file_as_path = os.path.join(self.path, legend_file_as_path)
        
        svg_ns = "{http://www.w3.org/2000/svg}"
        
        with open(abs_legend_file, 'r') as source_file:
            tree = etree.parse(source_file)
        
        node = tree.find('//{0}text[@id="Date"]/{0}tspan'.format(svg_ns))
        
        current_date = datetime.now()
        formatted_date = current_date.strftime('%d.%m.%Y')
        node.text = formatted_date
        
        logging.info(f'{self.name}: update {legend_file} with current date')
        
        with open(abs_legend_file, 'wb') as target:
            tree.write(target, encoding="utf-8", xml_declaration=True, pretty_print=True)
        
        logging.info(f'{self.name}: convert legend files\' text to path')
        
        inkscape_command = 'inkscape "{0}" --export-text-to-path --export-plain-svg -o "{1}"'.format(abs_legend_file, abs_legend_file_as_path)
        returned_output = subprocess.call(inkscape_command, shell=True)

    def __wait_until_map_build_is_finished(self):
        finished_successful = False
        timeout = time.time() + 60 * 10  # 10 minutes timeout

        while not finished_successful and time.time() < timeout:
            return_code, output = self.__execute_command('state')

            if return_code == 0:
                status_code_match = search(r'received status = \'(\d+) \w+\'', output)
                status_value = int(status_code_match.group(1) if status_code_match is not None else '-1')

                if status_value != 200:
                    time.sleep(5)
                    continue

                status_match = search(r'attend status of \'(\w+)\'', output)
                status = status_match.group(1) if status_match is not None else '<Not found>'
                if status == 'MapBuildSuccessful':
                    finished_successful = True
                    logging.info(f'{self.name}: map build finished successful')
                else:
                    logging.info(f'{self.name}: map build not finished yet')
                    time.sleep(30)

        if not finished_successful:
            logging.error(f'{self.name}: map build not finished and ran into timeout')

    def generate(self):
        self.__renew_map_id()
        self.__update_legend()
        
        logging.info(f'{self.name}: generate map ...')

        arguments = ['update', 'upload', 'order', 'download', 'unzip']
        for argument in arguments:
            return_code, output = self.__execute_command(argument)

            if return_code != 0:
                logging.error(f'{self.name}: action "{argument}" was not successful:\n{output}')

            if argument == 'order':
                self.__wait_until_map_build_is_finished()

            time.sleep(5)
        
        time.sleep(5)
    
    def __str__(self):
        return f'Map(\'{self.path}\')'
        

if __name__ == "__main__":
    log_format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=log_format, level=logging.INFO, datefmt="%H:%M:%S")
    logging.getLogger().setLevel(logging.DEBUG)
    
    folders_to_ignore = ['bin', 'shared']
    current_dir_path = os.path.dirname(os.path.realpath(__file__))

    # get all top level directories without folders to ignore and hidden '.*' folders
    toplevel_directories = [os.path.join(current_dir_path, p) for p in next(os.walk(current_dir_path))[1] if p not in
                            folders_to_ignore and p[0] != '.' and p[0] != '_']

    maps = [MapDefinition(d) for d in toplevel_directories]

    with ThreadPoolExecutor(max_workers=len(maps)) as executor:
        futures = [executor.submit(current_map.generate) for current_map in maps]
        wait(futures, timeout=60*10, return_when=ALL_COMPLETED)  # ALL_COMPLETED is actually the default

    logging.info("Finished.")
