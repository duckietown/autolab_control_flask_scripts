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
            raise ValueError(msg)
        return device_list

    except IOError as e:
        msg = 'Could not read from %s' % input_file
        print(msg)


def show_status(device_list, results):
    if debugging:
        fmt_header = '\t {:<4}{:<20}|{:<4}{:<20} '
        fmt_cell = '\t|{:<4}{:<20}|{:<4}{:<20}|'
        fmt_separator = ['=' * 4, '=' * 20, '=' * 4, '=' * 20]
        # print header
        print(fmt_header.format(*fmt_separator))
        print(fmt_cell.format('', 'Device', '', 'Status'))
        print(fmt_cell.format(*fmt_separator))
        # print one row per device
        for (res, device) in zip(results, device_list):
            print(fmt_cell.format('', device, '', res))
        # close table
        print(fmt_header.format(*fmt_separator))
