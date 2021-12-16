#!/usr/bin/env python3

# Author: Blastomussa
# Date 12/16/2021
# Example use case of FreshPy.py
# Put FreshPy.py in same directory as script to import
from FreshPy import FreshPy

# Initiates FreshPy class. Downloads all assets and filters for "Laptop" product type.
# Downloads all requesters from a specific requester group and then assigns assets to
# requesters according to last login on asset
def main():
    # initiate class
    api_key = '#############'
    FreshService_domain = 'https://customdomain.freshservice.com'
    FS = FreshPy(api_key, FreshService_domain)

    # download asset types
    types = FS.list_asset_types()
    for type in types:
        # filter for Laptops product type
        if(type['name']=='Laptop'):
            laptop_id = type['id']

    #dowload all assets
    assets = FS.list_assets(type_fields=True)
    laptops = []
    for asset in assets:
        # filter for Laptops product type
        if(asset['asset_type_id']==laptop_id):
            laptops.append(asset)

    # download staff
    # domain specific group ID; needs to be changed if running on different domain
    staff = FS.requester_group_members(17000056500)
    
    # interate through laptops to set Used By field for asset
    for laptop in laptops:
        print(laptop['name'])
        FS.lastUser2usedBy_staff(laptop, staff)
        sleep(1)

        
if __name__ == '__main__':
    main()
