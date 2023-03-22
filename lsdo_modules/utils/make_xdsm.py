from pytikz.dsm import DSM


def make_xdsm(data_dict, name='dsm'):
    dsm = DSM()

    diagonals = data_dict['diagonals']
    off_diagonals = data_dict['off_diagonals']


    dsm.write('dsm')

