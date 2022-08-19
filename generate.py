#!/usr/bin/env python

import logging
import os
import subprocess
from lxml import etree
from datetime import datetime
import time
import concurrent.futures


printmaps = os.path.abspath('./bin/printmaps')

class MapDefinition:
    def __init__(self, path):
        if not os.path.exists(path) or not os.path.isdir(path):
            raise "path %s is not a directory" % path
        
        self.path = os.path.abspath(path)
        self.name = os.path.basename(path)
        
    
    def __execute_command(action):
        
        logging.info(f'{self.name}: call \'{action}\'')
        
        #result = subprocess.call([printmaps, action], shell=True)
        result = subprocess.run([printmaps, action], capture_output=True, shell=True, text=True, cwd=self.path)
        
        return result


    def __renew_map_id(self):
        filename = "map.id"
        abs_filename = os.path.join(self.path, filename)
                
        if os.path.exists(abs_filename):
            os.remove(abs_filename)
        
        logging.info(f'{self.name}: create {filename}')
        
        self.__execute_command('create')
    
    
    def __try_to_update(self):
        # returned_output = subprocess.check_output(command) # returns output as byte string
        returned_output = self.__execute_command('update')
        
        # using decode() function to convert byte string to string
        #parsed_output = returned_output.decode('utf-8')
        
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
        
        currDate = datetime.now()
        formatted_date = currDate.strftime('%d.%m.%Y')
        node.text = formatted_date
        
        logging.info(f'{self.name}: update {legend_file} with current date')
        
        with open(abs_legend_file, 'wb') as target:
            tree.write(target, encoding="utf-8", xml_declaration=True, pretty_print=True)
        
        logging.info(f'{self.name}: convert legend files\' text to path')
        
        inkscape_command = 'inkscape "{0}" --export-text-to-path --export-plain-svg -o "{1}"'.format(abs_legend_file, abs_legend_file_as_path)
        returned_output = subprocess.call(inkscape_command, shell = True)


    def generate(self):
        self.__renew_map_id()
        self.__update_legend()
        
        logging.info(f'{self.name}: generate map ...')
        
        # arguments = ['update', 'upload'] # , 'order', 'download', 'unzip'
        # for argument in arguments:
            
        #     returned_output = self.__execute_command(argument)
        
        #     # using decode() function to convert byte string to string
        #     parsed_output = returned_output.decode('utf-8')
        
        time.sleep(5)
        
        
    
    def __str__(self):
        return f'Map(\'{self.path}\')'
        

if __name__ == "__main__":
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")
    logging.getLogger().setLevel(logging.DEBUG)
    
    folders_to_ignore = ['bin', 'shared']
    current_dir_path = os.path.dirname(os.path.realpath(__file__))

    # get all top level directories without folders to ignore and hidden '.*' folders
    toplevel_directories = [os.path.join(current_dir_path, p) for p in next(os.walk(current_dir_path))[1] if p not in folders_to_ignore and p[0] != '.' and p[0] != '_']

    maps = [MapDefinition(d) for d in toplevel_directories]

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(maps)) as executor:
        for map in maps:
            executor.submit(map.generate)
    
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for map in maps:
            executor.submit(map.generate)
            
    logging.info("Finished.")
