from .. import conn


class BugReporter(object):
    def report(self, *args):
        args = args[0]
        args['details'] = args['details'].replace('\'', '\'\'')
        sql = ('INSERT INTO support (bug_type, details) '
               'VALUES ({type}, \'{details}\')').format(
                   type=args['type'], details=args['details'])
        conn.execute(sql)
