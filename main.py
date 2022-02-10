import os
import cgi
import upload_file
import re



def run_server(name):
    # Python 3 server example
    from http.server import BaseHTTPRequestHandler, HTTPServer
    import time

    hostName = "localhost"
    serverPort = 8080
    max_blank_lines_for_end_of_body = 3

    class ECHB_file_server(BaseHTTPRequestHandler):

        def __init__(self,var1,var2,var3):
            # initialise fields
            self.packages_path = r"packages/"

            # make directory of files
            file_names = self.list_files_for_download()
            # convert files to HTML, for use later
            self.packages_directory_content_HTML = self.convert_file_names_to_HTML(file_names)
            self.post_called = False
            # I have no idea what these variables are for, but I just pass them to the parent constructor
            super().__init__(var1,var2,var3)

        def do_GET(self):
            domain = self.parse_and_direct(self.path)
            if domain.__len__() > 0 \
                    and not self.post_called \
                    and not domain == "favicon.ico":

               if domain == "upload":
                   self.send_response(200)
                   self.send_header("Content-type", "text/html")
                   self.end_headers()
                   with open("html/upload.html", "r") as upload_html_text:
                       self.wfile.write(bytes(upload_html_text.read(), "utf-8"))
               else:
                    self.send_response(200)
                    self.send_header("Content-type", "text")
                    self.send_header("Content-Disposition", "attachment; filename=%s" % domain)
                    self.end_headers()
                    with open(self.packages_path + domain,"rb") as file_stream:
                            lines = file_stream.readlines()
                            for line in lines:
                                print(line)
                                self.wfile.write(line)
            else: #if no resource is requested
               self.send_response(200)
               self.send_header("Content-type", "text/html")
               self.end_headers()
               with open("html/index.html", "r") as index_html_text:
                   self.wfile.write(bytes(index_html_text.read(), "utf-8"))
                   self.wfile.write(bytes(self.packages_directory_content_HTML, "utf-8"))
                   self.wfile.write(bytes("</body>","utf-8"))
                   self.wfile.write(bytes("</html>","utf-8"))
            self.post_called = False

        def do_POST(self):
            print(self.requestline)
            print(self.headers)
            file_name = None

            # the Content-Type HTTP header contains the boundary string, which delineates between the header and the
            # body of the HTTP request from the client. It has the format:
            # 'Content-Type: multipart/form-data; boundary=---------------------------14183926835513496131290498722'
            # so the easiest way to parse this is to grab the header, and then split it across the equals sign.
            # Of course there may not be a boundary string which we catch for as well.

            has_boundary = False
            content_type_header = self.headers.get("Content-Type")
            if content_type_header is not None:
                boundary_string = (str.split(self.headers.get("Content-Type"),'=')[1])
                if not self.headers.get("Content-Type").__contains__("boundary"):
                    print("warning, there is no boundary! File reading likely corrupted")
                else:
                    has_boundary = True


            HTTP_data = self.rfile
            num_blank_lines_crossed = 0

            with open("packages/temp.txt", "wt") as temp_file:
                is_start_boundary_crossed = False
                is_empty_line_crossed = False
                while True:
                    line = HTTP_data.readline()
                    print(str(line))
                    if line.__contains__(bytes("Content-Disposition:","utf-8")):
                        pattern = "(?:filename)=\"(.*)\""
                        result = re.search(pattern, line.decode())
                        file_name = result.group(1)
                    if has_boundary and line.__contains__(bytes(boundary_string, "utf-8")): # determine the end of HTTP body
                        if not is_start_boundary_crossed:
                            is_start_boundary_crossed = True
                            continue
                        if is_start_boundary_crossed:
                            break
                    elif line == b"\r\n": # HTTP bodies are delineated from the headers by an empty line.
                        is_empty_line_crossed = True
                        continue
                    elif line == b"":
                        num_blank_lines_crossed += 1
                        if num_blank_lines_crossed == max_blank_lines_for_end_of_body:
                            break
                    if is_empty_line_crossed:
                        temp_file.write(line.decode())

            if file_name is not None:
                with open("packages/" + file_name,'w') as permanent_file:
                    with open("packages/temp.txt", 'r') as temp_file:
                        for line in temp_file:
                            permanent_file.write(line)
            else:
                print("error locating the file name")
            # os.remove(temp_file.name)


            print("closed the file")
            self.post_called = True
            #self.do_GET()

        def list_files_for_download(self):
            #scan the packages directory to see what there is
            files =[]
            with os.scandir(self.packages_path) as dirs:
                for entry in dirs:
                    files.append(entry.name)
            return files

        def convert_file_names_to_HTML(self, files):

            HTML = ""
            for file in files:
                HTML = HTML + ("<a href=" + self.packages_path + file +" download= " + file +
                            "> Download file: " + file + "</a><br>")
            return HTML

        def parse_and_direct(self, path_str):
            dirs = path_str.split("/")
            return dirs[len(dirs)-1]

    if __name__ == "__main__":

        webServer = HTTPServer((hostName, serverPort), ECHB_file_server)
        print("Server started http://%s:%s" % (hostName, serverPort))

        try:
            webServer.serve_forever()
        except KeyboardInterrupt:
            pass

        webServer.server_close()
        print("Server stopped.")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    run_server('PyCharm')

# See PyCharm help at https://www.jetbrains.com/help/pycharm/

