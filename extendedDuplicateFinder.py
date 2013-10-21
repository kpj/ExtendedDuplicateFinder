from beets.plugins import BeetsPlugin
from beets.ui import Subcommand
from beets.library import Item


####################
# Helper Functions #
####################

def force_unicode(s):
    """Forces returned string to be unicode
    """
    if isinstance(s, str):
        return s.decode("utf8")
    return s

def check_key(key_list, items):
    """Creates dictionary which contains the matching attributes
		(as the key) and a list of the concerned items (as the value)
    """
    matches = {}
    for i in items:
        matches.setdefault(
                "-".join(
                    [
                        str(i[key]) 
                        if i[key] == None or isinstance(
													i[key], (int, long, float, complex)
												)
                        else force_unicode(i[key])
                        for key in key_list
                    ]
                ), []
            ).append(i)
    return matches

def gen_keylist(opts):
    """Generates list of all Item() attributes
    """
    return [
            k 
            for k in Item().keys()
            if (bool(opts["negate_all_options"]) ^ bool(opts[k])) or
            opts["compare_all"]
        ]

def gen_parser(cmd):
    """Creates cmdline argument parser which contains each Item()
		attribute and a couple of additional parameters
    """
    cmd.parser.add_option(
        '--delete',
        dest = 'actually_delete_files',
        action = 'store_true',
        help = 'Not only list, but actually erase items '
				'from database and disk'
    )
    cmd.parser.add_option(
        '--negate',
        dest = 'negate_all_options',
        action = 'store_true',
        help = 'Negate all passed options, e.g. "--title --negate" '
				'would compare everything but the title '
				'(has no effect with --all)'
    )
    cmd.parser.add_option(
        '--all',
        dest = 'compare_all',
        action = 'store_true',
        help = 'Compares all available options, i.e. only finds '
				'exact matches (takes precedence over --negate)'
    )

    for k in Item().keys():
        cmd.parser.add_option(
            '--%s' % k,
            dest = k,
            action = 'store_true',
            help = 'Check for duplicate %ss' % k
        )

def remove_item(item, lib):
    """Erases specified item from database and disk
    """
    lib.remove(item, delete = True, with_album = True)

def dupl_finder(lib, opts, args):
    """Lists and possibly deletes duplicates
    """
    res = check_key(gen_keylist(vars(opts)), lib.items(query = args))
    for key, match_list in res.iteritems():
        if len(match_list) > 1:
            # found duplicates
            for match in match_list:
                print "%s - %s - %s" % (
                        match["title"], 
                        match["artist"],
                        match["album"]
                    )
            print ""


#######################
# Command Declaration #
#######################

find_command = Subcommand(
    'find_duplicates', 
    help = 'Lists all duplicates for given query', 
    aliases = ["fdup"]
)
find_command.func = dupl_finder

gen_parser(find_command)


#####################
# Plugin Definition #
#####################

class ExtendedDuplicateFinder(BeetsPlugin):
    def commands(self):
        return [find_command]
