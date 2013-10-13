from beets.plugins import BeetsPlugin
from beets.ui import Subcommand
from beets.library import Item


####################
# Helper Functions #
####################

def check_key(key_list, items):
	""" Creates dictionary which contains the matching attributes (as the key) and a list of the concerned items (as the value) """
	matches = {}
	for i in items:
		matches.setdefault("-".join([str(i[key]) if isinstance(i[key], (int, long, float, complex)) else i[key].encode('utf8') for key in key_list]), []).append(i)
	return matches

def gen_keylist(opts):
	""" Generates list of all Item() attributes """
	return [k for k in Item().keys() if k in opts and opts[k]]

def gen_parser(cmd):
	""" Creates cmdline argument parser which contains each Item() attribute and a couple of additional parameters """
	cmd.parser.add_option(
		'--delete',
		dest = 'actually_delete_files',
		action = 'store_true',
		help = 'Not only list, but actually erase items from database and disk'
	)

	for k in Item().keys():
		cmd.parser.add_option(
			'--%s' % k,
			dest = k,
			action = 'store_true',
			help = 'Check for duplicate %ss' % k
		)

def remove_item(item, lib):
	""" Erases specified item from database and disk """
	lib.remove(item, delete = True, with_album = True)

def dupl_finder(lib, opts, args):
	""" Lists and possibly deletes duplicates """
	res = check_key(gen_keylist(vars(opts)), lib.items(query = args))
	for key, match_list in res.iteritems():
		if len(match_list) > 1:
			# found duplicates
			for match in match_list:
				print "%s - %s - %s" % (match["title"], match["artist"], match["album"])
			print ""


#######################
# Command Declaration #
#######################

find_command = Subcommand('find_duplicates', help = 'Lists all duplicates for given query', aliases = ["fdup"])
find_command.func = dupl_finder

gen_parser(find_command)


#####################
# Plugin Definition #
#####################

class ExtendedDuplicateFinder(BeetsPlugin):
	def commands(self):
		return [find_command]
