'''
Created on Jul 29, 2012

@author: Mikael
'''
from collections import defaultdict
import os


class KWGraph(object):
    class KWNode(object):
        def __init__(self, kw):
            self.kw = kw
            self.edgeout = set()
            self.edgein = set()

        def __str__(self):
            return 'KWNode(%s)' % self.kw

    class KWEdge(object):
        def __init__(self, n1, n2, w):
            self.n1, self.n2 = n1, n2
            self.weight = w
            n1.edgeout.add(self)
            n2.edgein.add(self)

        def __str__(self):
            return 'KWEdge(%s, %s)' % (self.n1, self.n2)

    def __init__(self):
        self.format_map = {}
        self.nodes = {}
        self.edges = {}

    def getNode(self, kw):
        if kw not in self.nodes:
            self.nodes[kw] = self.KWNode(kw)
        return self.nodes[kw]

    def makeEdge(self, kw1, kw2, weight=1.0):
        n1, n2 = self.getNode(kw1), self.getNode(kw2)
        self.edges[(kw1, kw2)] = self.KWEdge(n1, n2, weight)

    def deleteEdge(self, edge):
        '''
        Delete edge specified by either kw tuple or by KWEdge instance.
        '''
        if not isinstance(edge, self.KWEdge):
            edge = self.edges.get(edge)
        if edge:
            edge.n1.edgeout.discard(edge)
            edge.n2.edgein.discard(edge)
            self.edges.pop(edge, None)

    def restrict(self, roots=None, th_top=99):
        '''
        Returns a subset graph from roots.
        '''
        roots = roots or self.findRoots()
        level = self.top_sort(roots)
        graph = KWGraph()

        for kw1, kw2, w in self.walkEdgesDF(roots):
            if kw2 not in level:
                raise ValueError('No level for %s' % kw2)

            if level[kw2] <= th_top:
                graph.makeEdge(kw1, kw2, w)

        graph.format_map = self.format_map

        return graph

    def top_sort(self, roots=None):
        '''
        Topological sorting {kw->level} for all nodes.
        '''
        level = defaultdict(int)
        roots = roots or self.findRoots()

        for kw1, kw2, _ in self.walkEdgesDF(roots):

            if kw1 not in level:
                level[kw1] = 0

            level[kw2] = max(level[kw1] + 1, level[kw2])

        return level

    def bottom_sort(self):
        '''
        Reversed topological sorting {kw->rlevel} for all nodes.
        '''
        level = defaultdict(int)
        roots = self.findRoots()

        for kw1, kw2, _ in self.walkEdgesDF(roots):
            if kw2 not in level:
                level[kw2] = 0

            level[kw1] = max(level[kw2] + 1, level[kw1])

        return level

    def findNeighbours(self, kw):
        nodes = [e.n2 for e in self.nodes[kw].edgeout]
        return [n.kw for n in nodes]

    def findRoots(self):
        return [nn.kw for nn in self.nodes.values() if not nn.edgein]

    def findLeaves(self):
        return [nn.kw for nn in self.nodes.values() if not nn.edgeout]

    def findLeafClusters(self):
        '''
        Decide how to group leafs into clusters according to parent set.
        '''
        leafclusters = defaultdict(set)

        for kw in self.findLeaves():
            node = self.getNode(kw)
            parentstr = '_'.join(e.n1.kw for e in node.edgein)
            parentstr = u'nodecluster_%s' % parentstr.encode('ascii', 'ignore').replace(
                ' ', '_').translate(None, '.,:\'-').encode(
                'utf-8')
            leafclusters[parentstr].add(kw)

        return leafclusters

    def parents_of(self, kw):
        """
        Find all parents for a node.
        """
        nn = self.getNode(kw)
        return [e.n1.kw for e in nn.edgein]

    def children_of(self, kw):
        """
        Find all parents for a node.
        """
        nn = self.getNode(kw)
        return [e.n2.kw for e in nn.edgeout]

    def ancestry_of(self, kw):
        """
        Find all roots for a node.
        """
        pending = [kw]
        ancestry = []
        while pending:
            kkw = pending.pop()
            parents = self.parents_of(kkw)
            if kkw not in parents:
                ancestry.append(kkw)
            pending.extend(parents)
        return ancestry

    def roots_of(self, kw):
        """
        Find all roots for a node.
        """
        return [kkw for kkw in self.ancestry_of(kw) if not self.getNode(kkw).edgein]

    def format_node(self, kw):
        """
        Format a node label for output.
        """
        kw = self.format_map.get(kw, kw)
        return kw

    def make_dot_graph_lines(self, roots=None, th_top=10, th_bottom=0):
        '''
        Graphvizard dot-format graph representation, returns two lists of str lines: nodes and edges.
        
        th_top : int
            Nodes must be at most this many levels from a root.
            
        th_bottom : int
            Nodes must be at least this many levels from a leaf.
             
        '''
        level = self.top_sort()
        rlevel = self.bottom_sort()
        roots = roots or self.findRoots()
        kwset = set(kw for kw in self.walkNodesDF(roots) if th_top >= level[kw] and th_bottom <= rlevel[kw])
        kw_miss = set(kw for kw in self.walkNodesDF(roots) if kw not in kwset)
        leafclusters = self.findLeafClusters()

        for k, vs in leafclusters.items():
            leafclusters[k] = [kw for kw in vs if kw in kwset]
            if len(leafclusters[k]) < 1:
                del leafclusters[k]

        leafmap = dict((kw, k) for k, vset in leafclusters.items() for kw in vset)
        clusteredgecount = defaultdict(int)
        clusterused = set()
        nodelines = []
        edgelines = []

        ## write all the edges not going to clusters
        for kw1, kw2, _weight in self.walkEdgesDF(roots):
            if kw1 in kwset and kw2 in kwset:
                kwid1 = u'n_%s' % kw1.encode('ascii', 'ignore').replace(' ', '_').translate(None, '.,:\'-')
                kwid2 = u'n_%s' % kw2.encode('ascii', 'ignore').replace(' ', '_').translate(None, '.,:\'-')
                if kw2 in leafmap:
                    clusteredgecount[(kwid1, leafmap[kw2])] += 1
                else:
                    edgelines.append(u'''\t%s -> %s;''' % (kwid1, kwid2))

        ## write all edges going to clusters
        for (kwid1, clusterid), count in clusteredgecount.items():
            weight = max(2, min(8, count))
            edgelines.append(u'''\t%s -> %s [weight=%d];''' % (kwid1, clusterid, weight))
            clusterused.add(clusterid)

        ## write all the clusters of leaf nodes
        for parentstr, leafset in leafclusters.items():
            if parentstr in clusterused:
                columns = []
                rows = []
                linelen = 0

                for kw in sorted(leafset):
                    bgcolor = '0.0 0.0 0.950'
                    kwid = u'n_%s' % kw.encode('ascii', 'ignore').replace(' ', '_').translate(None, '.,:\'-')
                    fs = int(10)
                    pw = max(1, fs / 18)

                    kwlabel = self.format_node(kw)
                    columns.append(kwlabel)
                    linelen += len(kwlabel)

                    if linelen >= 120:
                        rows.append('%s' % '|'.join(columns))
                        columns = []
                        linelen = 0

                if columns:
                    rows.append('%s' % '|'.join(columns))

                label = u'|'.join('{%s}' % r for r in rows) #.encode('utf-8')
                nodelines.append(
                    u'\t\t%s [label="%s",fontsize=%d,shape=record,fontname=Arial,style="rounded,filled",fillcolor="%s"];' % (
                    parentstr, label, 12, bgcolor))

        ## write all the non-clustered nodes
        for kw in sorted(kwset):
            if kw not in leafmap:
                kwid = u'n_%s' % kw.encode('ascii', 'ignore').replace(' ', '_').translate(None, '.,:\'-').encode(
                    'utf-8')
                kwlabel = self.format_node(kw)

                fs = int(max(10, 24 - 4 * level[kw]))
                pw = max(1, fs / 18)
                bgcolor = '0.0 0.0 0.975'

                nodelines.append(
                    u'\t%s [label="%s",fontsize=%d,shape=egg,fontname=Arial,margin="0.01,0.01",penwidth="%f",style=filled,fillcolor="%s"];' % (
                    kwid, kwlabel, fs, pw, bgcolor))

        return nodelines, edgelines

    def make_dot_graph(self, path, fname, roots=None, th_top=99, th_bottom=0):
        '''
        Graphvizard dot-format graph representation, writes it to file.
        '''
        dotfile = os.path.join(path, fname + '.dot')
        nodelines, edgelines = self.make_dot_graph_lines(roots=roots, th_top=th_top, th_bottom=th_bottom)

        with open(dotfile, "w+") as fh:
            fh.write(
                '''digraph AllThemes {
                    size="30,200";
                    margin=1;
                    nodesep=0.05;
                    ranksep=1;
                    rankdir=LR;
                    rotate=0;
                    center=1;
                    overlap="false";
                    compound=true;
                    concentrate=true;
                ''')
            fh.write(u'\n'.join(nodelines).encode('utf-8'))
            fh.write(u'\n'.join(edgelines).encode('utf-8'))
            fh.write(u'''\n}\n''')

        return dotfile

    def _walkEdgesDF(self, rnode, done):
        '''
        Walk edges from a node, loops broken arbitrarily and all edges below root returned exactly once.
        '''
        if not rnode in done:
            done.add(rnode)
            for edge in rnode.edgeout:
                yield edge
                for ee in self._walkEdgesDF(edge.n2, done):
                    yield ee

    def walkEdgesDF(self, roots):
        '''
        Walk edges from a set of root keywords, loops broken arbitrarily and all edges below root returned exactly once.
        '''
        done = set()
        for rnode in [self.nodes[rkw] for rkw in roots if rkw in self.nodes]:
            for ee in self._walkEdgesDF(rnode, done):
                yield (ee.n1.kw, ee.n2.kw, ee.weight)

        for rkwmiss in [rkw for rkw in roots if rkw not in self.nodes]:
            raise ValueError('Root {} not found in graph nodes'.format(rkwmiss))

    def walkNodesDF(self, roots):
        '''
        Walk nodes from a set of root keywords, loops broken arbitrarily and all nodes below root returned exactly once.
        '''
        keywords = set()

        for kw1, kw2, _ in self.walkEdgesDF(roots):
            keywords.update([kw1, kw2])

        return keywords

    def _trimShortcuts(self, rnode, done):
        '''
        Trim shortcuts in a DAG, remove any edge P->C if there is a longer path P->...->C.
        '''
        # recursively trim for children
        done.add(rnode)

        for edge in rnode.edgeout:
            self._trimShortcuts(edge.n2, done)

        # remove any edge to a child reachable from another child
        for edge in list(rnode.edgeout):
            deleted = False
            for other in rnode.edgeout - set([edge]):
                for ee in self._walkEdgesDF(other.n2, set()):
                    if edge.n2 == ee.n2:
                        self.deleteEdge(edge)
                        deleted = True
                        break
                if deleted:
                    break

    def trimShortcuts(self):
        '''
        Trim shortcuts in a DAG, remove any edge P->C if there is a longer path P->...->C.
        '''
        for root in self.findRoots():
            self._trimShortcuts(self.nodes[root], done=set())
