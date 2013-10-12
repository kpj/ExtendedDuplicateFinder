from beets.plugins import BeetsPlugin
from beets.ui import Subcommand
from beets.library import Item


# helper functions
def check_key(key_list, items):
	matches = {}
	for i in items:
		res = []
		for key in key_list:
			cur = i[key]
			if isinstance(cur, (int, long, float, complex)): # TODO: make this more elegant
				res.append(str(cur))
			else:
				res.append(cur.encode('utf8'))
		matches.setdefault("-".join(res), []).append(i)
	return matches

def gen_keylist(opts):
	out = []
	for k in Item().keys():
		if k in opts and opts[k]:
			out.append(k)
	return out

def gen_parser(cmd):
	for k in Item().keys():
		cmd.parser.add_option(
			'--%s' % k,
			dest = k,
			action = 'store_true',
			help = 'Check for duplicate %ss' % k
		)

def remove_item(item, lib):
	lib.remove(item, delete = True, with_album = True)

def dupl_finder(lib, opts, args):
	res = check_key(gen_keylist(vars(opts)), lib.items(query = args))
	for key, match_list in res.iteritems():
		if len(match_list) > 1:
			# found duplicates
			for match in match_list:
				print "%s - %s - %s" % (match["title"], match["artist"], match["album"])
			print ""

# declare command
find_command = Subcommand('find_duplicates', help = 'Lists all duplicates for given query', aliases = ["fdup"])
find_command.func = dupl_finder

# set option parser
gen_parser(find_command)

# actual plugin
class ExtendedDuplicateFinder(BeetsPlugin):
	def commands(self):
		return [find_command]
