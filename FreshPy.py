#!/usr/bin/env python3

# Author: Blastomussa
# Date 12/13/2021
# Class based implementation of FreshService API
import requests
from sys import exit
from time import sleep

# Add limiting to stay under api rate: https://support.freshservice.com/support/solutions/articles/50000000293-what-is-the-rate-limit-for-apis-across-all-plans-
# Add better error handling; maybe switch statement for status codes on exit()
# Add intuituve pagination handling
# Error handling for bad uri's, dead connection, failed auth, api rate, bad jsons

class FreshPy(object):
    """
        Takes api key and custom domain of freshservice instance as arguments
    """
    # args: FreshService API Key and FreshService domain URL
    def __init__(self, api_key, root_uri):
        self.key = api_key
        self.root_uri = root_uri + '/api/v2'


    #------------------- Raw API Requests -------------------#
    # arg: API URI
    # return: requests.response object
    def _get(self, uri):
        response = requests.get(uri, auth=(self.key,''))
        if(response.status_code!=200): exit(str(response.status_code) + " Error")
        return response


    # arg: API URI; json data(python dict object)
    # return: requests.response object
    def _post(self, uri, data):
        headers={
            'Content-type':'application/json',
            'Accept':'application/json'
        }
        response = requests.post(uri, headers=headers, auth=(self.key,''), json=data)
        if(response.status_code!=200 and response.status_code!=201):
            exit(str(response.status_code) + " Error")
        return response


    # arg: API URI; json data(python dict object)
    # return: requests.response object
    def _put(self, uri, data):
        headers={
            'Content-type':'application/json',
            'Accept':'application/json'
        }
        response = requests.put(uri, headers=headers, auth=(self.key,''), json=data)
        if(response.status_code!=200 and response.status_code!=204):
            exit(str(response.status_code) + " Error")
        return response


    # arg: API URI
    # return: requests.response object
    def _delete(self, uri):
        response = requests.delete(uri, auth=(self.key,''))
        if(response.status_code!=200 and response.status_code!=204):
            exit(str(response.status_code) + " Error")
        return response


    #------------------- Pagination -------------------#
    # arg: requests.response object
    # return: next_page URI or None
    def _paginate(self, response):
        header = response.headers
        try:
            link = header['link']
            start = link.find('<')
            end = link.find('>')
            url = link[start+1:end]
            return url
        except(KeyError):
            return None


    #------------------- Tickets Calls -------------------#
    # arg:
    # return:
    def create_ticket(self, data):
        uri = self.root_uri + '/tickets'
        response = self._post(uri, data)
        return response.json()['ticket']


    # arg:
    # return:
    def view_ticket(self, ticket_id):
        uri = self.root_uri + '/tickets/' + str(ticket_id)
        response = self._get(uri)
        return response.json()['ticket']


    # arg:
    # return:
    # test and optimize; keep under api limit
    def all_tickets(self):
        uri = self.root_uri + '/tickets?per_page=100'
        response = self._get(uri)
        tickets = response.json()['tickets']
        next_page = self._paginate(response)
        while(next_page!=None):
            response = self._get(next_page)
            t = response.json()['tickets']
            tickets = tickets + t
            next_page = self._paginate(response)
            sleep(.5) #to keep under api rate limit
        return tickets


    # arg:
    # return:
    def update_ticket(self, ticket_id, data):
        uri = self.root_uri + '/tickets/' +  str(ticket_id)
        response = self._put(uri, data)
        return response.json()['ticket']


    # arg:
    # return:
    def delete_ticket(self, ticket_id):
        uri = self.root_uri + '/tickets/' + str(ticket_id)
        response = self._delete(uri)
        return "Successfully deleted ticket: {}".format(ticket_id)


    #------------------- Requester Calls -------------------#
    # arg:
    # return:
    def create_requester(self, data):
        uri = self.root_uri + '/requesters'
        response = self._post(uri, data)
        return response.json()['requester']


    # arg:
    # return: requester json
    def view_requester(self, email=None, id=None):
        if(email!=None): uri = self.root_uri + '/requesters?email=' + email
        if(id!=None): uri = self.root_uri + '/requesters/' + str(id)
        response = self._get(uri)
        return response.json()['requesters']


    # optional arg: per page(integer 1-100)
    # return: list of requster jsons
    def all_requesters(self, per_page=100):
        uri = self.root_uri + '/requesters?per_page=' + str(per_page)
        response = self._get(uri)
        requesters = response.json()['requesters']
        # pagination handling
        next_page = self._paginate(response)
        while(next_page!=None):
            response = self._get(next_page)
            r = response.json()['requesters']
            requesters = requesters + r
            next_page = self._paginate(response)
        return requesters
    
    
    # arg:
    # return:
    def requester_fields(self):
        uri = self.root_uri + '/requester_fields'
        response = self._get(uri)
        return response.json()['requester_fields']


    # arg:
    # return:
    def update_requester(self, requester_id, data):
        uri = self.root_uri + '/requesters/' + str(requester_id)
        response = self._post(uri, data)
        return response.json()['requester']


    # arg:
    # return:
    def deactivate_requester(self, requester_id):
        uri = self.root_uri + '/requesters/' + str(requester_id)
        response = self._delete(uri)
        return "Successfully deactivated requester: {}".format(requester_id)


    # arg:
    # return:
    def delete_requester(self, requester_id):
        uri = self.root_uri + '/requesters/' + str(requester_id) + '/forget'
        response = self._delete(uri)
        return "Successfully deleted requester: {}".format(requester_id)
    
    
    # arg:
    # return:
    def requester2agent(self,requester_id):
        uri = self.root_uri + '/requesters/' + str(requester_id) + '/convert_to_agent'
        response = self._put(uri, None)
        return response.json()['agent']
    
    
    # arg:
    # return:
    def merge_requesters(self,requester_id, secondary_id):
        uri = self.root_uri + '/requesters/'+ str(requester_id) + '/merge?secondary_requesters=' + str(secondary_id)
        response = self._put(uri,None)
        return response.json()['requester']
    
    
    # arg:
    # return:
    def reactivate_requesters(self,requester_id):
        uri = self.root_uri + '/requesters/'+ str(requester_id) + '/reactivate'
        response = self._put(uri,None)
        return response.json()['requester']


    #------------------- Agents Calls -------------------#
    # arg:
    # return:
    def create_agent(self, data):
        uri = self.root_uri + '/agents'
        response = self._post(uri, data)
        return response.json()['agent']


    # arg:
    # return:
    def view_agent(self, email=None, agent_id=None):
        if(email!=None): uri = self.root_uri + '/agents?email=' + email
        if(agent_id!=None): uri = self.root_uri + '/agents/' + str(agent_id)
        response = self._get(uri)
        return response.json()['agent']


    # arg:
    # return:
    def all_agents(self):
        uri = self.root_uri + '/agents'
        response = self._get(uri)
        agents = response.json()['agents']
        # pagination handling
        next_page = self._paginate(response)
        while(next_page!=None):
            response = self._get(next_page)
            r = response.json()['agents']
            agents = agents + r
            next_page = self._paginate(response)
        return agents


    # arg:
    # return:
    def update_agent(self, agent_id, data):
        uri = self.root_uri + '/agents/' + str(agent_id)
        response = self._put(uri, data)
        return response.json()['agent']
    
    
    # arg:
    # return:
    def deactivate_agent(self, agent_id):
        uri = self.root_uri + '/agents/' + str(agent_id)
        response = self._delete(uri)
        return "Successfully deactivated agent: {}".format(agent_id)
    
    
    # arg:
    # return:
    def forget_agent(self, agent_id):
        uri = self.root_uri + '/agents/' + str(agent_id) + '/forget'
        response = self._delete(uri)
        return "Successfully deleted agent: {}".format(agent_id)
    
    
    # arg:
    # return:
    def reactivate_agent(self, agent_id):
        uri = self.root_uri + '/agents/' + str(agent_id) + '/reactivate'
        response = self._put(uri,None)
        return response.json()['agent']
    
    
    # arg:
    # return:
    def agent2requester(self, agent_id):
        uri = self.root_uri + '/agents/' + str(agent_id) + '/convert_to_requester'
        response = self._put(uri,None)
        return response.json()['requester']
    
    
    # arg:
    # return:
    def agent_fields(self):
        uri = self.root_uri + '/agent_fields'
        response = self._get(uri)
        return response.json()['agent_fields']
    
    
    #------------------- Agent Role Calls -------------------#
    # arg:
    # return:
    def (self, role_id):
        uri = self.root_uri + '/roles/' + str(role_id)
        response = self._get(uri)
        return response.json()['role']


    # arg:
    # return:
    def all_roles(self):
        uri = self.root_uri + '/roles'
        response = self._get(uri)
        return response.json()['roles']

    
    #------------------- Agent Group Calls -------------------#
    # arg:
    # return:
    def create_agent_group(self, group_json):
        uri = self.root_uri + '/groups'
        response = self._post(uri, group_json)
        return response.json()['group']


    # arg:
    # return:
    def view_agent_group(self, group_id):
        uri = self.root_uri + '/groups/' + str(group_id)
        response = self._get(uri)
        return response.json()['group']


    # arg:
    # return:
    def all_agent_groups(self):
        uri = self.root_uri + '/groups'
        response = self._get(uri)
        return response.json()['groups']


    # arg:
    # return:
    def update_agent_group(self, group_id, data):
        uri = self.root_uri + '/groups/' + str(group_id)
        response = self._put(uri, data)
        return response.json()['group']


    # arg:
    # return:
    def delete_agent_group(self, group_id):
        uri = self.root_uri + '/groups/' + str(group_id)
        response = self._delete(uri)
        return "Successfully deleted agent group: {}".format(group_id)


    #------------------- Requester Group Calls -------------------#
    # arg:
    # return:
    def create_requester_group(self, data):
        uri = self.root_uri + '/requester_groups'
        response = self._post(uri, data)
        return response.json()['requester_group']

    # arg:
    # return:
    def view_requester_group(self, group_id):
        uri = self.root_uri + '/requester_groups/' + str(group_id)
        response = self._get(uri)
        return response.json()['requester_group']


    # optional arg: per page(integer 1-100)
    # return: requester group json
    def all_requester_groups(self, per_page=100):
        uri = self.root_uri + '/requester_groups?per_page=' + str(per_page)
        response = self._get(uri)
        return response.json()

    # arg:
    # return:
    def update_requester_group(self, group_id, data):
        uri = self.root_uri + '/requester_groups/' + str(group_id)
        response = self._put(uri, data)
        return response.json()['requester_group']


    # arg:
    # return:
    def delete_requester_group(self, group_id):
        uri = self.root_uri + '/requester_groups/' + str(group_id)
        response = self._delete(uri)
        return "Successfully deleted requester_group: {}".format(group_id)
    
    
    # arg:
    # return:
    def add_group_member(self, group_id, requester_id):
        uri = self.root_uri+ '/requester_groups/'+ str(group_id) +'/members/' + str(requester_id)
        response = self._post(uri, None)
        return "Successfully added requester: {0} to group: {1}".format(requester_id, group_id)
    
    
    # arg:
    # return:
    def delete_group_member(self, group_id, requester_id):
        uri = self.root_uri + '/requester_groups/' + str(group_id) + '/members/' + str(requester_id)
        response = self._delete(uri)
        return "Successfully removed requester: {0} from requester_group: {1}".format(group_id,requester_id)


    # arg: group id(integer)
    # optional arg: per page(integer 1-100)
    # return: list of requester jsons
    def requester_group_members(self, group_id, per_page=100):
        uri = self.root_uri+ '/requester_groups/'+ str(group_id) +'/members?per_page=' + str(per_page)
        response = self._get(uri)
        requesters = response.json()['requesters']
        # pagination handling
        next_page = self._paginate(response)
        while(next_page!=None):
            response = self._get(next_page)
            r = response.json()['requesters']
            requesters = requesters + r
            next_page = self._paginate(response)
        return requesters
        
    
    #------------------- Product Calls -------------------#
    # arg:
    # return:
    def create_product(self, data):
        uri = self.root_uri + '/products'
        response = self._post(uri, data)
        return response.json()['product']


    # arg:
    # return:
    def view_product(self, product_id):
        uri = self.root_uri + '/products/' + str(product_id)
        response = self._get(uri)
        return response.json()['product']


    # arg:
    # return:
    def all_products(self):
        uri = self.root_uri + '/products'
        response = self._get(uri)
        return response.json()['products']


    # arg:
    # return:
    def update_products(self, product_id, data):
        uri = self.root_uri + '/products/' + str(product_id)
        response = self._put(uri, data)
        return response.json()['product']


    # arg:
    # return:
    def delete_product(self, product_id):
        uri = self.root_uri + '/products/' + str(product_id)
        response = self._delete(uri)
        return "Successfully deleted product: {}".format(product_id)
    
    
    #------------------- Vendor Calls -------------------#
    # arg:
    # return:
    def create_vendor(self, data):
        uri = self.root_uri + '/vendors'
        response = self._post(uri, data)
        return response.json()['vendor']

    # arg:
    # return:
    def view_vendor(self, vendor_id):
        uri = self.root_uri + '/vendors/' + str(vendor_id)
        response = self._get(uri)
        return response.json()['vendor']


    # arg:
    # return:
    def all_vendors(self):
        uri = self.root_uri + '/vendors'
        response = self._get(uri)
        return response.json()['vendors']


    # arg:
    # return:
    def update_vendor(self, vendor_id, data):
        uri = self.root_uri + '/vendors/' + str(vendor_id)
        response = self._put(uri, data)
        return response.json()['vendor']


    # arg:
    # return:
    def delete_vendor(self, vendor_id):
        uri = self.root_uri + '/vendors/' + str(vendor_id)
        response = self._delete(uri)
        return "Successfully deleted vendor: {}".format(vendor_id)


    #------------------- Asset Calls -------------------#
    # arg:
    # return: list of asset jsons
    def list_assets(self, type_fields=False, per_page=100):
        uri = self.root_uri + '/assets?per_page=' + str(per_page)
        if(type_fields==True):
            uri = uri + '&include=type_fields'
        response = self._get(uri)
        assets = response.json()['assets']
        # pagination handling
        next_page = self._paginate(response)
        while(next_page!=None):
            response = self._get(next_page)
            r = response.json()['assets']
            assets = assets + r
            next_page = self._paginate(response)
        return assets


    # arg:
    # return: asset json
    def view_asset(self, display_id, type_fields=False):
        uri = self.root_uri + '/assets/' + str(display_id)
        if(type_fields==True):
            uri = uri + '?include=type_fields'
        response = self._get(uri)
        asset_data = response.json()['asset']
        return asset_data


    # arg:
    # return: asset json
    def update_asset(self, display_id, data):
        uri = self.root_uri + '/assets/' + str(display_id)
        response = self._put(uri, data)
        return response.json()['asset']


    # arg:
    # return: Success message or Error
    def delete_asset(self, display_id):
        uri = self.root_uri + '/assets/' + str(display_id)
        response = self._delete(uri)
        return "Successfully deleted asset {}".format(display_id)


    # arg:
    # return: Success message or Error
    def perm_delete_asset(self, display_id):
        uri = self.root_uri + '/assets/' + str(display_id) + "/delete_forever"
        response = self._put(uri, None)
        return "Permanently deleted asset {}".format(display_id)


    #------------------- Asset Type Calls -------------------#
    # arg:
    # return:
    def list_asset_types(self):
        uri = self.root_uri + '/asset_types?per_page=100'
        response = self._get(uri)
        return response.json()['asset_types']


    #------------------- Author Specific Functions -------------------#
    # last_login_by field needs to be updated if run on different freshservice domain
    # can this be optimized?
    # Last user is AzureAD user(FirstnameLastname) and requesters are synced from Google
    def lastUser2usedBy_staff(self, asset, requester_list):
        asset_id = asset['display_id']
        last_login = str(asset['type_fields']['last_login_by_17000000908'])
        if(asset['type_fields']['last_login_by_17000000908']==None): return
        for requester in requester_list:
            requester_name = str(requester['first_name']) + str(requester['last_name'])
            if(last_login.lower()==requester_name.lower()):
                data = {'user_id': int(requester['id'])}
                response = self.update_asset(asset_id,data)
                print(response)


    # match email for google synced requesters to Chromebook last sign in email
    # last_login_by field needs to be updated if run on different freshservice domain
    def lastUser2usedBy_students(self, asset, requester_list):
        asset_id = asset['display_id']
        last_login = str(asset['type_fields']['last_login_by_17000000908'])
        if(asset['type_fields']['last_login_by_17000000908']==None): return
        for requester in requester_list:
            requester_email = str(requester['primary_email'])
            if(last_login.lower()==requester_email.lower()):
                data = {'user_id': int(requester['id'])}
                response = self.update_asset(asset_id,data)
                print(response)
