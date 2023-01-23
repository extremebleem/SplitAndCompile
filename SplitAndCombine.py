import os, re
class SplitAndCombineFiles:
    
    def __init__(self):
        self.__input_file_name = None
        self.__chunk = None
        self.__postfix = '.ros'
        self.f_size = 0
        self.check_list = ""

    def get_file_chunks_from_count(self):
        """ This method is to get the file chunk sizes"""
        # get the file zize
        self.f_size = os.path.getsize(self.__input_file_name)
        print("Total file Size : {}".format(str(self.f_size)))

        # get the file chunks
        f_chunk = int(float(self.f_size) / float(self.__chunk))
        print("Splitting into {} files of {} size".format(str(self.__chunk),
                                                        str(f_chunk)))
        return int(f_chunk), int(self.__chunk)

    def get_file_count_from_size(self):
        """ This method is to get the file chunk sizes"""

        size = {"b": 1, "kb": 1024, "mb": 1024 ** 2, "gb": 1024 ** 3}

        # get the file zize
        self.f_size = os.path.getsize(self.__input_file_name)
        print("Total file Size : {}".format(str(self.f_size)))

        # get the file chunks
        f_chunk = re.sub("\D", "", self.__chunk)
        size_type = self.__chunk.replace(f_chunk, "")
        f_chunk = int(f_chunk) * size[size_type]
        no_of_files = self.f_size / f_chunk
        if no_of_files > 1:
            no_of_files = int(no_of_files) + 1 if \
                no_of_files%int(no_of_files) > 0 \
                else int(no_of_files)
        else:
            no_of_files = 1

        print("Splitting into {} files of {} size".format(str(no_of_files),
                                                        str(self.__chunk)))

        return int(f_chunk), int(no_of_files)

    def __split(self, input_file_name, chunk_size):
        self.__input_file_name = input_file_name
        self.__chunk = chunk_size

        print("Splitting the File Now")

        if self.__chunk.isdigit():
            f_chunk, chunk_size = self.get_file_chunks_from_count()
        else:
            f_chunk, chunk_size = self.get_file_count_from_size()

        # read the content of the main file
        read_main_file = open(self.__input_file_name, "rb")
        tot_bytes_in_file = 0

        # Iterate through chunk size
        for i in range(int(chunk_size)):
            _chunk_file_name = "{}-{}{}".format(str(self.__input_file_name),
                                                str(i+1),
                                                str(self.__postfix))

            # Last chunk , include the remaining data
            if i == chunk_size - 1:
                f_chunk = self.f_size - tot_bytes_in_file

            # Read the chunks from the file
            data = read_main_file.read(f_chunk)

            # create the content for the file copy check
            data_length = len(data)
            self.check_list += str(data[:5]) + str(
                data[int(data_length / 2) - 1:
                     int(data_length / 2) + 1]) + str(data[-5:])

            tot_bytes_in_file += data_length

            # Write the chunks to the file
            print("Creating {}".format(_chunk_file_name))
            with open(_chunk_file_name, "wb") as _:
                _.write(data)

        _crc_file_name = "{}-{}{}".format(str(self.__input_file_name),
                                          "CRC", str(self.__postfix))

        print("Creating the check file : {}".format(str(_crc_file_name)))
        with open(_crc_file_name, "w") as crc_file:
            crc_file.write(self.check_list)

        print("File split successfully")

    def __merge(self, input_file_name):
        print("Merging the file to {}".format(str(input_file_name)))

        _root_dir, _file_name = os.path.split(
            os.path.realpath(input_file_name))

        _file_path = os.path.join(_root_dir, _file_name)

        if os.path.exists(_file_path):
            print("File Already Exist. Please remove the {} and "
                "then re-run.".format(str(_file_path)))

            # Prompt if file need to be deleted automatically
            prompt = input("\nDo you want to remove the file [Y/N] : ")
            if prompt.strip().lower() == "y":
                os.remove(_file_path)
            else:
                return

        # get all the split files available
        file_list = self.get_split_files(_root_dir, _file_name)
        if not file_list:
            print("No Split files found")
            return

        # get the crc file
        _crc_file_name = "{}-{}{}".format(str(_file_name),
                                          "CRC", str(self.__postfix))

        _crc_file_path = os.path.join(_root_dir,_crc_file_name)
        if not os.path.exists(_crc_file_path):
            print("{} file is missing".format(str(_crc_file_path)))
            return

        _crc_data = open(_crc_file_path, "r").read()

        for files in sorted(file_list):
            f_name = file_list[files]
            print("Merging the file {}".format(f_name))
            with open(input_file_name, 'ab') as new_file:
                data = open(os.path.join(_root_dir,
                                         f_name), 'rb').read()

                new_file.write(data)

                # create the content for the file copy check
                data_length = len(data)
                self.check_list += str(data[:5]) + \
                                   str(data[int(data_length/2)-1:
                                            int(data_length/2)+1]) \
                                   + str(data[-5:])
        # check the crc data
        print("Checking if the files are merged properly")
        if _crc_data == self.check_list:
            print("File check : Passed")
        else:
            print("File check : Failed.")
            return

        print("File Merged successfully")

    def get_split_files(self, root_dir, file_name):
        file_list = {}

        file_format = re.compile(file_name + '-' + '[0-9]+'+self.__postfix)
        for f in os.listdir(root_dir):
            if file_format.match(f):
                _ = f.split('-')[-1]
                _ = int(re.sub('\D', '', _))
                file_list[_] = f

        return file_list

    def split(self, input_file_name):
        self.__split(input_file_name, '8gb')

    def merge(self, input_file_name):
        self.__merge(input_file_name)
       
