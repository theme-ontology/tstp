from collections import defaultdict
import webobject


def get_metatheme_data():
	"""
	@returns
		data: { theme => [(sid1, weight1), ...], ...},
		parents: { theme => [parent1, ...] },
		toplevel: [ theme1, ...],
	"""
	themes = webobject.Theme.load()
	storythemes = webobject.StoryTheme.load()
	parent_lu = {}
	toplevel = set()
	data = defaultdict(set)
	ret_data = {}

	for theme in themes:
		parent_lu[theme.name] = [ t.strip() for t in theme.parents.split(",") ]

	for st in storythemes:
		theme_stack = [ st.name2 ]
		item = (st.name1, st.weight)

		while theme_stack:
			theme = theme_stack.pop()
			data[theme].add(item)

			if theme in parent_lu:
				theme_stack.extend(parent_lu[theme])
			else:
				toplevel.add(theme)

	for key, items in data.iteritems():
		ret_data[key] = sorted(items)

	toplevel = sorted(toplevel)

	return ret_data, parent_lu, toplevel


if __name__ == '__main__':
    get_metatheme_data()



