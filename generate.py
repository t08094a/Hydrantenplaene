#!/usr/bin/env python

import os
import subprocess
from lxml import etree
from datetime import datetime


printmaps = "bin/printmaps"


class MapDefinition:
    def __init__(self, path):
        if not os.path.exists(path) or not os.path.isdir(path):
            raise "path %s is not a directory" % path
        
        self.path = os.path.abspath(path)


    def __renew_map_id(self):
        filename = "map.id"
        abs_filename = os.path.join(self.path, filename)
        command = "%s %s", printmaps, "create"
        
        if os.path.exists(abs_filename):
            os.delete(abs_filename)
        
        print("create %s" % filename)
        os.exec(command)
    
    
    def __try_to_update(self):
        command = '{0} {1}'.format(printmaps, 'update')
        
        # returned_value = subprocess.call(command, shell=True)  # returns the exit code in unix
        returned_output = subprocess.check_output(command) # returns output as byte string
        
        # using decode() function to convert byte string to string
        parsed_output = returned_output.decode('utf-8')
        
        
        print('Result:', parsed_output)
        
        pass
    
    
    def update_legend(self):
        legend_file = 'legend.svg'
        legend_file_as_path = 'legend-path.svg'
        
        abs_legend_file = os.path.join(self.path, legend_file)
        abs_legend_file_as_path = os.path.join(self.path, legend_file_as_path)
        
        svg_ns = "{http://www.w3.org/2000/svg}"
        
        with open(abs_legend_file, 'r') as source_file:
            tree = etree.parse(source_file)
        
        node = tree.find('//{0}text[@id="Date"]/{0}tspan'.format(svg_ns))
        print('n=', node)
            
        currDate = datetime.now()
        formatted_date = currDate.strftime('%d.%m.%Y')
        node.text = formatted_date
        
        print('update {0} with current date'.format(legend_file))
        
        with open(abs_legend_file, 'wb') as target:
            tree.write(target, encoding="utf-8", xml_declaration=True, pretty_print=True)
        
        print('svg: convert text to path')
        inkscape_command = 'inkscape "{0}" --export-text-to-path --export-plain-svg -o "{1}"'.format(abs_legend_file, abs_legend_file_as_path)
        returned_output = subprocess.call(inkscape_command, shell = True)
        print('inkscape returned {0}'.format(returned_output))
        
        
    

    def generate(self):
        command = "%s %s", printmaps, "update"
        
        print("generate map %s ..." % self.path.name)
        
    
    def __str__(self):
        return f'Map(\'{self.path}\')'
        

folders_to_ignore = ['bin', 'shared']
current_dir_path = os.path.dirname(os.path.realpath(__file__))

# get all top level directories without folders to ignore and hidden '.*' folders
toplevel_directories = [os.path.join(current_dir_path, p) for p in next(os.walk(current_dir_path))[1] if p not in folders_to_ignore and p[0] != '.' and p[0] != '_']

maps = [MapDefinition(d) for d in toplevel_directories]

for map in maps:
    print('update map', map.path)
    map.update_legend()
