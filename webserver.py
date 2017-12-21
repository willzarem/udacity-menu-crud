import cgi
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from urlparse import unquote

import re
from sqlalchemy import create_engine, orm

from database_setup import Base, Restaurant


class webServerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        try:
            if self.path.endswith('/restaurants'):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                engine = create_engine('sqlite:///restaurantmenu.db')

                Base.metadata.bind = engine
                session = orm.sessionmaker(bind=engine)()

                output = '''
                    <html>
                    <body>
                        <h1>Restaurants!</h1>
                        <ul>
                            %s
                        </ul>
                        
                        <a href="/restaurants/new">Add new</a>
                    </body>
                    </html>
                '''
                list = ''
                for restaurant in session.query(Restaurant).all():
                    list += '''
                        <li>
                            <span>{}</span>
                            <a href="/restaurants/{}/edit">Edit</a>
                            <a href="/restaurants/{}/delete">Delete</a>
                        </li>
                    '''.format(restaurant.name, restaurant.id, restaurant.id)

                self.wfile.write(output % list)
                return

            if self.path.endswith('/restaurants/new'):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                output = '''
                    <html>
                    <body>
                        <h1>New Restaurant:</h1>
                        <form method="POST" enctype="multipart/form-data">
                            <label for="name">Name:</label>
                            <input id="name" name="name" type="text" />
                            <input type="submit" />
                        </form>
                        <a href="/restaurants">Back to restaurants.</a>
                    </body>
                    </html>
                '''
                self.wfile.write(output)
                print(output)
                return

            if re.match(pattern='/restaurants/[0-9]+/edit', string=self.path):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                engine = create_engine('sqlite:///restaurantmenu.db')

                Base.metadata.bind = engine
                session = orm.sessionmaker(bind=engine)()

                restaurant_id = self.path.split('/')[2]
                restaurant = session.query(Restaurant).filter_by(
                    id=restaurant_id).one()

                output = '''
                    <html>
                    <body>
                        <h1>Edit Restaurant: {}</h1>
                        <form method="POST" enctype="multipart/form-data">
                            <label for="name">Name:</label>
                            <input id="name" name="name" type="text" value="{}"/>
                            <input type="submit" />
                        </form>
                        <a href="/restaurants">Back to restaurants.</a>
                    </body>
                    </html>
                '''.format(restaurant.name, restaurant.name)
                self.wfile.write(output)
                print(output)
                return

            if re.match(pattern='/restaurants/[0-9]+/delete', string=self.path):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()

                engine = create_engine('sqlite:///restaurantmenu.db')

                Base.metadata.bind = engine
                session = orm.sessionmaker(bind=engine)()

                restaurant_id = self.path.split('/')[2]
                restaurant = session.query(Restaurant).filter_by(
                    id=restaurant_id).one()

                output = '''
                    <html>
                    <body>
                        <h1>Are you sure you want to delete {}?</h1>
                        <form method="POST" enctype="multipart/form-data">
                            <input type="submit" value="Delete"/>
                        </form>
                        <a href="/restaurants">Back to restaurants.</a>
                    </body>
                    </html>
                '''.format(restaurant.name)
                self.wfile.write(output)
                print(output)
                return

        except IOError:
            self.send_error(404, 'File not found %s' % self.path)

    def do_POST(self):
        try:
            if self.path.endswith('/restaurants/new'):

                engine = create_engine('sqlite:///restaurantmenu.db')

                Base.metadata.bind = engine
                session = orm.sessionmaker(bind=engine)()

                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    restaurant = Restaurant(name=fields.get('name')[0])
                    session.add(restaurant)
                    session.commit()

                self.send_response(301)
                self.send_header('Location', '/restaurants')
                self.end_headers()
                return
            if re.match(pattern='/restaurants/[0-9]+/edit', string=self.path):
                engine = create_engine('sqlite:///restaurantmenu.db')

                Base.metadata.bind = engine
                session = orm.sessionmaker(bind=engine)()

                ctype, pdict = cgi.parse_header(
                    self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    restaurant_id = self.path.split('/')[2]
                    restaurant = session.query(Restaurant).filter_by(
                        id=restaurant_id).one()
                    restaurant.name = fields.get('name')[0]
                    session.add(restaurant)
                    session.commit()

                self.send_response(301)
                self.send_header('Location', '/restaurants')
                self.end_headers()
            if re.match(pattern='/restaurants/[0-9]+/delete', string=self.path):
                engine = create_engine('sqlite:///restaurantmenu.db')

                Base.metadata.bind = engine
                session = orm.sessionmaker(bind=engine)()

                restaurant_id = self.path.split('/')[2]
                restaurant = session.query(Restaurant).filter_by(
                    id=restaurant_id).one()
                session.delete(restaurant)
                session.commit()

                self.send_response(301)
                self.send_header('Location', '/restaurants')
                self.end_headers()
        except:
            pass


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webServerHandler)
        print('Web server running on port %s' % port)
        server.serve_forever()
    except KeyboardInterrupt:
        print('^C entered. Stopping service...')
        server.socket.close()


if __name__ == '__main__':
    main()
