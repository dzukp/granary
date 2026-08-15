from aspiration import Aspiration
from engine import Engine
from general_system import GeneralSystem
from releaser import Releaser
from silo import Silo
from siren import Siren
from sound import Sound
from top import Top
from valve import Valve

mechanisms = {
    'conveyer_1_2': {
        'class': Engine,
        'mb_cells_idx': 50,
        'do_start': 'do_21_1',
        'di_ready': 'di_1_1',
        'di_started': 'di_1_2',
        'next_mechanisms': ['noria_3_3'],
    },
    'conveyer_1_3': {
        'class': Engine,
        'mb_cells_idx': 60,
        'do_start': 'do_21_2',
        'di_ready': 'di_1_3',
        'di_started': 'di_1_4',
        'next_mechanisms': ['conveyer_6_1'],
    },
    'noria_3_4': {
        'class': Engine,
        'mb_cells_idx': 70,
        'do_start': 'do_21_3',
        'di_ready': 'di_19_1',
        'di_started': 'di_19_2',
    },
    'fan_13_1': {
        'class': Engine,
        'mb_cells_idx': 80,
        'do_start': 'do_21_4',
        'di_ready': 'di_1_7',
        'di_started': 'di_1_8',
    },
    # А1 (DI) / А21 (DO) - noria_3.5 использует последние входы А1
    'noria_3_5': {
        'class': Engine,
        'mb_cells_idx': 90,
        'do_start': 'do_21_5',
        'di_ready': 'di_1_7',
        'di_started': 'di_1_8',
    },
    # А2 (DI) / А21 (DO)
    'noria_3_6': {
        'class': Engine,
        'mb_cells_idx': 100,
        'do_start': 'do_21_6',
        'di_ready': 'di_2_1',
        'di_started': 'di_2_2',
    },
    'conveyer_6_10': {
        'class': Engine,
        'mb_cells_idx': 110,
        'do_start': 'do_21_7',
        'di_ready': 'di_2_3',
        'di_started': 'di_2_4',
    },
    'conveyer_6_9': {
        'class': Engine,
        'mb_cells_idx': 120,
        'do_start': 'do_21_8',
        'di_ready': 'di_2_5',
        'di_started': 'di_2_6',
    },
    # А2 (DI) / А22 (DO)
    'noria_3_3': {
        'class': Engine,
        'mb_cells_idx': 130,
        'do_start': 'do_22_1',
        'di_ready': 'di_2_7',
        'di_started': 'di_2_8',
    },
    # А3 (DI) / А22 (DO)
    'fan_14': {
        'class': Engine,
        'mb_cells_idx': 140,
        'do_start': 'do_22_2',
        'di_ready': 'di_3_1',
        'di_started': 'di_3_2',
    },
    'fan_13_2': {
        'class': Engine,
        'mb_cells_idx': 150,
        'do_start': 'do_22_3',
        'di_ready': 'di_3_3',
        'di_started': 'di_3_4',
    },
    'fan_13_3': {
        'class': Engine,
        'mb_cells_idx': 160,
        'do_start': 'do_22_4',
        'di_ready': 'di_3_5',
        'di_started': 'di_3_6',
    },
    'fan_13_4': {
        'class': Engine,
        'mb_cells_idx': 170,
        'do_start': 'do_22_5',
        'di_ready': 'di_3_7',
        'di_started': 'di_3_8',
    },
    # А4 (DI) / А22 (DO)
    'fan_13_5': {
        'class': Engine,
        'mb_cells_idx': 180,
        'do_start': 'do_22_6',
        'di_ready': 'di_4_1',
        'di_started': 'di_4_2',
    },
    'fan_13_6': {
        'class': Engine,
        'mb_cells_idx': 190,
        'do_start': 'do_22_7',
        'di_ready': 'di_4_3',
        'di_started': 'di_4_4',
    },
    'fan_13_7': {
        'class': Engine,
        'mb_cells_idx': 200,
        'do_start': 'do_22_8',
        'di_ready': 'di_4_5',
        'di_started': 'di_4_6',
    },
    # А4 (DI) / А23 (DO)
    'fan_13_8': {
        'class': Engine,
        'mb_cells_idx': 210,
        'do_start': 'do_23_1',
        'di_ready': 'di_4_7',
        'di_started': 'di_4_8',
    },
    # --- Панель 2 ---
    # А5 (DI) / А24 (DO)
    'conveyer_1_4': {
        'class': Engine,
        'mb_cells_idx': 220,
        'do_start': 'do_24_1',
        'di_ready': 'di_5_1',
        'di_started': 'di_5_2',
    },
    'conveyer_6_1': {
        'class': Engine,
        'mb_cells_idx': 230,
        'do_start': 'do_24_2',
        'di_ready': 'di_5_3',
        'di_started': 'di_5_4',
    },
    'conveyer_1_8': {
        'class': Engine,
        'mb_cells_idx': 240,
        'do_start': 'do_24_3',
        'di_ready': 'di_5_5',
        'di_started': 'di_5_6',
    },
    'conveyer_1_7': {
        'class': Engine,
        'mb_cells_idx': 250,
        'do_start': 'do_24_4',
        'di_ready': 'di_5_7',
        'di_started': 'di_5_8',
    },
    # А6 (DI) / А24 (DO)
    'conveyer_6_2': {
        'class': Engine,
        'mb_cells_idx': 260,
        'do_start': 'do_24_5',
        'di_ready': 'di_6_1',
        'di_started': 'di_6_2',
    },
    'conveyer_1_6': {
        'class': Engine,
        'mb_cells_idx': 270,
        'do_start': 'do_24_6',
        'di_ready': 'di_6_3',
        'di_started': 'di_6_4',
    },
    'conveyer_1_5': {
        'class': Engine,
        'mb_cells_idx': 280,
        'do_start': 'do_24_7',
        'di_ready': 'di_6_5',
        'di_started': 'di_6_6',
    },
    'conveyer_1_9': {
        'class': Engine,
        'mb_cells_idx': 290,
        'do_start': 'do_24_8',
        'di_ready': 'di_6_7',
        'di_started': 'di_6_8',
    },
    # А7 (DI) / А25 (DO)
    'conveyer_1_10': {
        'class': Engine,
        'mb_cells_idx': 300,
        'do_start': 'do_25_1',
        'di_ready': 'di_7_1',
        'di_started': 'di_7_2',
    },
    'conveyer_1_11': {
        'class': Engine,
        'mb_cells_idx': 310,
        'do_start': 'do_25_2',
        'di_ready': 'di_7_3',
        'di_started': 'di_7_4',
    },
    'conveyer_1_12': {
        'class': Engine,
        'mb_cells_idx': 320,
        'do_start': 'do_25_3',
        'di_ready': 'di_7_5',
        'di_started': 'di_7_6',
    },
    'conveyer_6_5': {
        'class': Engine,
        'mb_cells_idx': 330,
        'do_start': 'do_25_4',
        'di_ready': 'di_7_7',
        'di_started': 'di_7_8',
    },
    # А8 (DI) / А25 (DO)
    'conveyer_6_11': {
        'class': Engine,
        'mb_cells_idx': 340,
        'do_start': 'do_25_5',
        'di_ready': 'di_8_1',
        'di_started': 'di_8_2',
    },
    'conveyer_6_4': {
        'class': Engine,
        'mb_cells_idx': 350,
        'do_start': 'do_25_6',
        'di_ready': 'di_8_3',
        'di_started': 'di_8_4',
    },
    'conveyer_6_6': {
        'class': Engine,
        'mb_cells_idx': 360,
        'do_start': 'do_25_7',
        'di_ready': 'di_8_5',
        'di_started': 'di_8_6',
    },
    'conveyer_6_8': {
        'class': Engine,
        'mb_cells_idx': 370,
        'do_start': 'do_25_8',
        'di_ready': 'di_8_7',
        'di_started': 'di_8_8',
    },
    'sluice_16_3': {
        'class': Engine,
        'mb_cells_idx': 380,
        'do_start': 'do_26_1',
        'di_ready': 'di_10_1',
        'di_started': 'di_10_2',
    },
    'valve_8_9': {
        'class': Valve,
        'mb_cells_idx': 390,
        'do_open': 'do_26_2',
        'do_close': 'do_26_3',
        'di_ready': 'di_10_3',
        'di_opened': 'di_10_4',
        'di_closed': 'di_26_5',
    },
    'valve_8_8': {
        'class': Valve,
        'mb_cells_idx': 400,
        'do_open': 'do_26_4',
        'do_close': 'do_26_5',
        'di_ready': 'di_10_6',
        'di_opened': 'di_10_7',
        'di_closed': 'di_10_8',
    },
    # А11 (DI) / А26-А27 (DO)
    'valve_8_2': {
        'class': Valve,
        'mb_cells_idx': 410,
        'do_open': 'do_26_6',
        'do_close': 'do_26_7',
        'di_ready': 'di_11_1',
        'di_opened': 'di_11_2',
        'di_closed': 'di_11_3',
    },
    'valve_8_7': {
        'class': Valve,
        'mb_cells_idx': 420,
        'do_open': 'do_27_1',
        'do_close': 'do_27_2',
        'di_ready': 'di_11_4',
        'di_opened': 'di_11_5',
        'di_closed': 'di_11_6',
    },
    # А12 (DI) / А27 (DO)
    'valve_8_12': {
        'class': Valve,
        'mb_cells_idx': 430,
        'do_open': 'do_27_3',
        'do_close': 'do_27_4',
        'di_ready': 'di_12_1',
        'di_opened': 'di_12_2',
        'di_closed': 'di_12_3',
    },
    'valve_8_13': {
        'class': Valve,
        'mb_cells_idx': 440,
        'do_open': 'do_27_5',
        'do_close': 'do_27_6',
        'di_ready': 'di_12_4',
        'di_opened': 'di_12_5',
        'di_closed': 'di_12_6',
    },
    # А27 (DI) / А27 (DO)
    'fan_15_3': {
        'class': Engine,
        'mb_cells_idx': 520,
        'do_start': 'do_27_7',
        'di_ready': 'di_27_7',
        'di_started': 'di_27_8',
    },
    # А13 (DI) / А28 (DO)
    'valve_8_10': {
        'class': Valve,
        'mb_cells_idx': 450,
        'do_open': 'do_28_1',
        'do_close': 'do_28_2',
        'di_ready': 'di_13_1',
        'di_opened': 'di_13_2',
        'di_closed': 'di_13_3',
    },
    'conveyer_6_7': {
        'class': Engine,
        'mb_cells_idx': 530,
        'do_start': 'do_28_3',
        'di_ready': 'di_13_4',
        'di_started': 'di_13_5',
    },
    # --- Панель 4 ---
    # А14 (DI) / А29 (DO)
    'valve_8_11': {
        'class': Valve,
        'mb_cells_idx': 460,
        'do_open': 'do_29_1',
        'do_close': 'do_29_2',
        'di_ready': 'di_14_1',
        'di_opened': 'di_14_2',
        'di_closed': 'di_14_3',
    },
    'valve_8_1': {
        'class': Valve,
        'mb_cells_idx': 470,
        'do_open': 'do_29_3',
        'do_close': 'do_29_4',
        'di_ready': 'di_14_4',
        'di_opened': 'di_14_5',
        'di_closed': 'di_14_6',
    },
    # А14-А15 (DI) / А29 (DO)
    'valve_8_5': {
        'class': Valve,
        'mb_cells_idx': 480,
        'do_open': 'do_29_5',
        'do_close': 'do_29_6',
        'di_ready': 'di_14_7',
        'di_opened': 'di_14_8',
        'di_closed': 'di_15_1',
    },
    # А15 (DI) / А29-А30 (DO)
    'valve_8_6': {
        'class': Valve,
        'mb_cells_idx': 490,
        'do_open': 'do_29_7',
        'do_close': 'do_29_8',
        'di_ready': 'di_15_2',
        'di_opened': 'di_15_3',
        'di_closed': 'di_15_4',
    },
    'valve_8_3': {
        'class': Valve,
        'mb_cells_idx': 500,
        'do_open': 'do_30_1',
        'do_close': 'do_30_2',
        'di_ready': 'di_15_5',
        'di_opened': 'di_15_6',
        'di_closed': 'di_15_7',
    },
    # А16 (DI) / А30 (DO)
    'valve_8_4': {
        'class': Valve,
        'mb_cells_idx': 510,
        'do_open': 'do_30_3',
        'do_close': 'do_30_4',
        'di_ready': 'di_16_1',
        'di_opened': 'di_16_2',
        'di_closed': 'di_16_3',
    },
    # --- Силосы ---
    # А16-А18 (DI)
    'silo_11_1': {
        'class': Silo,
        'mb_cells_idx': 540,
        'di_bottom_level': 'di_16_5',
        'di_top_level': 'di_16_6',
    },
    'silo_11_2': {
        'class': Silo,
        'mb_cells_idx': 545,
        'di_bottom_level': 'di_16_7',
        'di_top_level': 'di_16_8',
    },
    'silo_11_3': {
        'class': Silo,
        'mb_cells_idx': 550,
        'di_bottom_level': 'di_17_1',
        'di_top_level': 'di_17_2',
    },
    'silo_11_4': {
        'class': Silo,
        'mb_cells_idx': 555,
        'di_bottom_level': 'di_17_3',
        'di_top_level': 'di_17_4',
    },
    'silo_11_5': {
        'class': Silo,
        'mb_cells_idx': 560,
        'di_bottom_level': 'di_17_5',
        'di_top_level': 'di_17_6',
    },
    'silo_11_6': {
        'class': Silo,
        'mb_cells_idx': 565,
        'di_bottom_level': 'di_17_7',
        'di_top_level': 'di_17_8',
    },
    'silo_11_7': {
        'class': Silo,
        'mb_cells_idx': 570,
        'di_bottom_level': 'di_18_1',
        'di_top_level': 'di_18_2',
    },
    'silo_11_8': {
        'class': Silo,
        'mb_cells_idx': 575,
        'di_bottom_level': 'di_18_3',
        'di_top_level': 'di_18_4',
    },
    'silo_12': {
        'class': Silo,
        'mb_cells_idx': 580,
        'di_bottom_level': 'di_18_5',
        'di_top_level': 'di_18_6',
    },
}


def pop_mechanisms(*names):
    global mechanisms
    return {name: mechanisms.pop(name) for name in names}


objects = {
    'top': {
        'class': Top,
        'mb_cells_idx': 1,
        'children': {
            'aspiration': {
                'class': Aspiration,
                'mb_cells_idx': 10,
                'children': {
                    **pop_mechanisms('sluice_16_3', 'fan_15_3'),
                },
            },
            'general_system': {
                'class': GeneralSystem,
                'mb_cells_idx': 20,
                'children': mechanisms,
                'di_silos_ready': 'di_16_4',
                'di_socket_1': 'di_9_1',
                'di_socket_2': 'di_9_2',
                'di_socket_3': 'di_9_3',
            },
            'siren': {
                'class': Siren,
                'mb_cells_idx': 585,
                'do_start': 'do_30_5',
            },
            'releaser': {
                'class': Releaser,
                'mb_cells_idx': 590,
                'do_release': 'do_23_2',
                'do_control_on': 'do_30_8',
                'di_explosion': 'di_18_8',
            },
            'sound': {
                'class': Sound,
                'mb_cells_idx': 595,
                'file_path': '../res/alarm.wav',
            },
        },
    },
}
