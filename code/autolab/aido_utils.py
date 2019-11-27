from typing import List
debugging = True


def get_device_list(input_file):
    device_list = []

    try:
        with open(input_file, 'r') as filestream:
            for line in filestream:
                hostname = line.rstrip()
                if hostname == '':
                    continue
                device_list.append(hostname)

        if len(device_list) == 0:
            msg = 'Could not find any device in %s' % input_file
            print(msg)
            raise CouldNotReadDeviceList(msg)
        return device_list

    except IOError as e:
        msg = 'Could not read from %s' % input_file
        print(msg)


def show_status(device_list, results):
    if debugging:
        print('\t {:<4}{:<20}|{:<4}{:<20} '.format(
            '=' * 4, '=' * 20, '=' * 4, '=' * 20))
        print('\t|{:<4}{:<20}|{:<4}{:<20}|'.format('', 'Device', '', 'Status'))
        print('\t|{:<4}{:<20}|{:<4}{:<20}|'.format(
            '=' * 4, '=' * 20, '=' * 4, '=' * 20))

        for (res, device) in zip(results, device_list):
            print('\t|{:<4}{:<20}|{:<4}{:<20}|'.format('', device, '', res))

        print('\t {:<4}{:<20}|{:<4}{:<20} '.format(
            '=' * 4, '=' * 20, '=' * 4, '=' * 20))
