# vim: set ts=4 sw=4 sts=4 et ai:
import imaplib
import re
from collections import OrderedDict
from django.conf import settings

#list_base_pattern = r'\((?P<flags>.*?)\) "(?P<delimiter>.*)" "(?P<name>[^"]*)"'
#list_response_pattern = re.compile(list_base_pattern)
#listextended_response_pattern = \
#        re.compile(list_base_pattern + r'\s*(?P<childinfo>.*)')
#unseen_pattern = re.compile(r'[^\(]+\(UNSEEN (\d+)\)')

list_response_pattern = re.compile(r'\((?P<flags>.*?)\) "(?P<delimiter>.*)" (?P<name>.*)')

def open_imap_connection(request, verbose=False):

    username = request.user.username
    password = request.session['_auth_user_password']
    host = settings.MAIL_SERVER

    # Connect to the server
    connection = imaplib.IMAP4_SSL(host)
    # Login to our acount
    connection.login(username, password)
    return connection

class BoxObject(object):
    '''
    A class that represents a mailbox.
    @param parent: the parent of a subfolder or None
    @param lookup_name: the imap given name to directly fetch the mailbox from 
                        the imap server
    @param name: the name of the mailbox used in the template
    '''
    parent = None
    lookup_name = None
    def __init__(self, name=None):
        self.name = name 

def parse_list(data):

    def parser(tree, nodes, lookup_name):
        def traverse(tree, nodes):
            # list of nodes for the current line in the received data 
            t_nodes = [n for n in nodes]

            for index, item in enumerate(t_nodes):
                try:
                    # Set the parent of the next item to the
                    # current item (might be handy in the future if
                    # we want a reference to the items parent if any).
                    t_nodes[index+1].parent = item
                except:
                    # this is the last item in the loop, so there is
                    # no need to go trough the `lookup_name` loop lateron in 
                    # this function, we can just use the input lookup_name.
                    item.lookup_name = lookup_name.strip('"')

                # Define old item
                old_item = None
                for x in tree.keys():
                    if x.name == item.name:
                        # keep a reference to the old itemso we can remove it
                        # from the nodes later ... we set the key item as item,
                        # this is done to reuse the same object we created
                        # earlier.
                        # exmaple situation: 
                        # ['Sent', 'temp']
                        # ['Sent, temp2']
                        # Both `Send` should have the same key in the tree,
                        # but since the objects are created dynamicly 
                        # its memory id isi different. meaning that the key 
                        # would be different, meaning we would end up with a 
                        # resulting 2 keys with both a value, instead of 1 key 
                        # with 2 values.
                        old_item = item
                        item = x

                if item not in tree:
                    # If the lookup name is not set means that this item has
                    # child items, we do want the lookup_name so we can query
                    # the mailserver for the folder contents, so we set it 
                    # for this subpart of the list.
                    if not item.lookup_name:
                        lookup_name_list = []
                        # make a list from the lookup_name
                        for x in [n.strip('"') for n in lookup_name.split('.')]:
                            # if we have a match ...
                            if item.name == x:
                                # ... append to the list and end the loop
                                lookup_name_list.append(x)
                                break
                            else:
                                # ...if not we add the item to the list.
                                lookup_name_list.append(x)
                        # Reconstruct the partial lookup_name for this mailbox
                        # folder
                        item.lookup_name = '.'.join(map(str, lookup_name_list))
                    # 
                    tree[item] = OrderedDict() 

                # remove the old item from the list if its set 
                if old_item:
                    t_nodes.remove(old_item)
                # if we have no old_item we can just remove our current item
                # from the list
                else:
                    t_nodes.remove(item)
                # And do the same loop again with our smaller list and pass an
                # empty dict (value from tree[item]) as tree to fill up!
                return traverse(tree[item], t_nodes)

        # Start the dictionary traversion
        traverse(tree, nodes)
        # return the resulting tree
        return tree


    tree = OrderedDict() 
    for line in reversed(data):
        flags, delimiter, mbox_name = list_response_pattern.match(line).groups() 
        nodes = [BoxObject(name=n.strip('"')) for n in mbox_name.split('.')]
        parser(tree, nodes, mbox_name)
    return tree
