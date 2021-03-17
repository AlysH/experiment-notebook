import os
from enb import icompression
from enb.config import get_options
import sortedcontainers

options = get_options()


class HEVC_lossless(icompression.WrapperCodec, icompression.LosslessCodec):
    def __init__(self, config_path=None, chroma_format="400"):
        config_path = config_path if config_path is not None \
            else os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              f"hevc_lossless_{chroma_format}.cfg")

        chroma_format = str(chroma_format)
        assert chroma_format in ["400"], f"Chroma format {chroma_format} not supported."

        icompression.WrapperCodec.__init__(
            self,
            compressor_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "TAppEncoderStatic"),
            decompressor_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "TAppDecoderStatic"),
            param_dict=dict(chroma_format=chroma_format))

        self.config_path = config_path

    def get_compression_params(self, original_path, compressed_path, original_file_info):
        return f"-i {original_path} -c {self.config_path} -b {compressed_path} -wdt {original_file_info['width']} " \
               f"-hgt {original_file_info['height']} -f {original_file_info['component_count']} " \
               f"-cf {self.param_dict['chroma_format']} --InputChromaFormat={self.param_dict['chroma_format']} " \
               f"--InputBitDepth={8 * original_file_info['bytes_per_sample']}"

    def get_decompression_params(self, compressed_path, reconstructed_path, original_file_info):
        return f"-b {compressed_path} -o {reconstructed_path} -d {8 * original_file_info['bytes_per_sample']}"

    @property
    def label(self):
        return "HEVC lossless"


class HEVC_lossy(icompression.WrapperCodec, icompression.LossyCodec):
    def __init__(self, config_path=None, chroma_format="400", qp=4):
        # TODO: this class repeats a lot of codde from HEVC_lossless
        # please  avoid duplicating code, e.g., call super().__init__() and defin
        # other functions as necessary

        # TODO: the config file did not exist. Please verify changes
        # in hevc_lossy_400.cfg and compare them to the recommened
        # values in https://vcgit.hhi.fraunhofer.de/jvet/HM/-/tree/master/cfg
        config_path = config_path if config_path is not None \
            else os.path.join(os.path.dirname(os.path.abspath(__file__)),
                              f"hevc_lossy_{chroma_format}.cfg")


        # TODO: no need for sorted containers here
        param_dict = sortedcontainers.SortedDict()

        # TODO: the value of QP should be validated in the __init__
        param_dict['QP'] = str(qp)
        chroma_format = str(chroma_format)
        param_dict['chroma_format'] = chroma_format

        assert chroma_format in ["400"], f"Chroma format {chroma_format} not supported."

        icompression.WrapperCodec.__init__(
            self,
            compressor_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "TAppEncoderStatic"),
            decompressor_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), "TAppDecoderStatic"),
            param_dict=param_dict)

        self.config_path = config_path

    def get_compression_params(self, original_path, compressed_path, original_file_info):
        if original_file_info['bytes_per_sample'] > 1:
            raise Exception(f"Bytes per sample = {original_file_info['bytes_per_sample']} not supported")
        else:
            return f"-i {original_path} -c {self.config_path} -b {compressed_path} -wdt {original_file_info['width']} " \
                   f"-hgt {original_file_info['height']} -f {original_file_info['component_count']} " \
                   f"-cf {self.param_dict['chroma_format']} --InputChromaFormat={self.param_dict['chroma_format']} " \
                   f"--InputBitDepth={8 * original_file_info['bytes_per_sample']} " \
                   f"-q {self.param_dict['QP']}"

    def get_decompression_params(self, compressed_path, reconstructed_path, original_file_info):
        if original_file_info['bytes_per_sample'] > 1:
            raise Exception(f"Bytes per sample = {original_file_info['bytes_per_sample']} not supported")
        else:
            return f"-b {compressed_path} -o {reconstructed_path} -d {8 * original_file_info['bytes_per_sample']}"

    @property
    def label(self):
        return "HEVC lossy"