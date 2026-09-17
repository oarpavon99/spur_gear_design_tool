from pprint import pprint
import json
import tkinter as tk
import tkinter.font as tkFont

def get_gear_ratios(input_data_in, module1, module2, module3):

    module_1 = module1
    module_2 = module2
    module_3 = module3

    torque_in = input_data_in['torque_in']
    rpm_in = input_data_in['rpm_in']
    torque_out = input_data_in['torque_out']
    diameter_hs = input_data_in['diameter_hs']
    diameter_axle = input_data_in['diameter_axle']
    delta1_in = input_data_in['delta_1']
    delta2_in = input_data_in['delta_2']

    # Defines the biggest pitch diameter allowed for the gear. In this case, 29 mm is chosen due to the available inner width (32 mm)
    # This would allow an outside diameter of approximately 30mm, leaving 1mm clearance on both sides of the gear
    teilkreis_max = 29
    print(f'diameter_axle= {diameter_axle}')
    # Defines the diameter of the Dowel pin used as the axle of the first 2 Stages of the gearbox, this defines the pitch diameter of the smallest gear
    if diameter_axle == 2:
        min_pitch_diameter = 5.5
        print(f'min_pitch_diameter: {min_pitch_diameter}')
    elif diameter_axle == 3:
        min_pitch_diameter = 6
        print(f'min_pitch_diameter: {min_pitch_diameter}')


    # Defines the number of teeth for the 6 gears used in the 3 stages of the gearbox
    # The first 2 driving gears and the third driven gear are set values, otherwise the possible number of combinations make the computer crash
    N1 = round(6 / module_1)
    N2_min, N2_max = round(min_pitch_diameter / module_1), round(teilkreis_max / module_1)
    N3 = round(min_pitch_diameter / module_2)
    N4_min, N4_max = round(min_pitch_diameter / module_2), round(teilkreis_max / module_2)
    N5_min = round(min_pitch_diameter / module_3)
    N6 = round(teilkreis_max / module_3)

    # Defines the gear ratio, considering that the torque output should be 3 Nm
    torque_in = torque_in
    rpm_in = rpm_in
    u_ratio = round(torque_out / torque_in, 3)
    print('u_ratio=', u_ratio)
    ratios_list = []
    ratios_filtered = []

    # Computes all the possible teeth number combinations, and pushes them all into a list called ratios_list
    for N2 in range(N2_min, N2_max):    # ESTE, con 10: for N2 in range(10, N2_max): OR for N2 in range(N2_min, N2_max):
        for N4 in range(N4_min, N4_max):
            for N5 in range(N5_min, N6+1):
                ratio = (N6*N4*N2)/(N5*N3*N1)
                teeth_number = {}
                teeth_number.setdefault('ratio', round(ratio, 2))
                teeth_number.setdefault('Z1', N1)
                teeth_number.setdefault('Z2', N2)
                teeth_number.setdefault('Z3', N3)
                teeth_number.setdefault('Z4', N4)
                teeth_number.setdefault('Z5', N5)
                teeth_number.setdefault('Z6', N6)
                ratios_list.append(teeth_number)
    ratios_list.sort(reverse='True', key=lambda x: x['ratio'])


    # Classifies all the ratios, to choose only those ones that fulfill the XX Conditions
    for element in ratios_list:
        # Condition 1: The gear ratio should be bigger than the necessary gear ratio to generate the 3 Nm desired output
        if element['ratio'] >= u_ratio:
            # Computes the distance between the pitch diameter 2 and the center of the dowel pin
            # If this condition would not be fulfilled then the dowel would colide with the gear, as it would go though it
            delta1 = (element['Z3']+element['Z4']) * module_2 - element['Z2'] * module_1
            delta1 = delta1/2
            # Computes the distance between the pitch diameter 4 and the hollow shaft
            # If this condition would not be fulfilled then the 4th gear would colide with the hollow shaft
            delta2 = (element['Z5']+element['Z6']) * module_3 - element['Z4'] * module_2 - diameter_hs
            delta2 = delta2/2
            # Computes the size of the gearbox if all gears would be aligned on a straight line, as the gearbox should be as small as possible
            gear_box_size = (element['Z1']+element['Z2']) * module_1 + (element['Z3'] + element['Z4']) * module_2 + (element['Z5'] + element['Z6']) * module_3
            torque_out = torque_in * element['ratio']
            rpm_out = rpm_in / element['ratio']
            # The computed values associated with each combination which gear ratio is bigger than the required gear ratio are pushed into a dictionary
            dictionary_results = {}
            dictionary_results.setdefault('delta1', round(delta1, 2))
            dictionary_results.setdefault('delta2', round(delta2, 2))
            dictionary_results.setdefault('torque_out', round(torque_out, 2))
            dictionary_results.setdefault('rpm_out', round(rpm_out, 2))
            dictionary_results.setdefault('module_1', module_1)
            dictionary_results.setdefault('module_2', module_2)
            dictionary_results.setdefault('module_3', module_3)
            dictionary_results.setdefault('gear_box_size', gear_box_size)
            dictionary_results.setdefault('diameter_hs', diameter_hs)

            if (delta1 >= delta1_in and                 # Condition 2: clearance between the pitch diameter 2 and dowel pin
                    delta2 >= delta2_in and             # Condition 3: clearance between the pitch diameter 4 and the hollow shaft
                    rpm_out > 30 and                    # Condition 4: at least 30 rpm
                    element['Z5'] < element['Z4']  and
                    element['Z1'] > 10 and              # Condition 6: manufacturable minimum teeth number = 10
                    element['Z3'] > 10):                # Condition 6: manufacturable minimum teeth number = 10
                element.update(dictionary_results)
                ratios_filtered.append(element)
    ratios_filtered.sort(reverse='True', key=lambda x: x['gear_box_size'])
    print(f'Posible combinations: {len(ratios_list)}')
    print(f'Posible combinations WITH CONDITIONS: {len(ratios_filtered)}')

    if  len(ratios_filtered):
        return ratios_filtered[len(ratios_filtered)-1]
    else:
        return None

def get_best_modules(input_data_in):
    # This function "grid-searches" all the possible module combinations by feeding the modules to the function "get_gear_ratios"
    modules = [0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    possible_combinations = []
    module3 = 0.3
    for module1 in modules:
        for module2 in modules:
            print('--------------------------------------------------------')
            print('module1 = ', module1, ' module2 = ', module2, ' module3 = 0.3')
            element=get_gear_ratios(input_data_in, module1, module2, module3)
            if element:
                possible_combinations.append(element)
    return possible_combinations

def create_gui_1():
    input_data = {}

    def run():
        torque_in_read = float(tk_torque_in.get())
        rpm_in_read = int(tk_rpm_in.get())
        torque_out_read = float(tk_torque_out.get())
        diameter_hs_read = float(tk_diameter_hs.get())
        diameter_axle_read = float(tk_diameter_axle.get())
        delta_1_read = float(tk_delta_1.get())
        delta_2_read = float(tk_delta_2.get())

        input_data.setdefault('torque_in', torque_in_read)
        input_data.setdefault('rpm_in', rpm_in_read)
        input_data.setdefault('torque_out', torque_out_read)
        input_data.setdefault('diameter_hs', diameter_hs_read)
        input_data.setdefault('diameter_axle', diameter_axle_read)
        input_data.setdefault('delta_1', delta_1_read)
        input_data.setdefault('delta_2', delta_2_read)

        print("Torque in:", input_data['torque_in'])
        print("rpm in:", input_data['rpm_in'])
        print("Torque out:", input_data['torque_out'])
        print("Hollowshaft external diameter:", input_data['diameter_hs'])
        print("Dowel Pin diameter:", input_data['diameter_axle'])
        print("Delta 1:", input_data['delta_1'])
        print("Delta 2:", input_data['delta_2'])
        window.destroy()

    window = tk.Tk()
    window.title('3-Stage Gearbox Designer')
    window.wm_iconbitmap('gear.ico')
    window.geometry("+%d+%d" %(100,100))

    torque_in = str(0.189)
    rpm_in = str(500)
    torque_out = str(3)
    diameter_hs = str(24)
    diameter_axle = str(3)
    delta_1 = str(5)
    delta_2 = str(2)

    main_frame = tk.Frame(window)
    main_frame.grid(row=0, column=0, padx=5, pady=5)
    frame_1 = tk.Frame(main_frame, padx=5, pady=5, bd=3, relief=tk.GROOVE)
    frame_1.grid(row=0, column=0)
    frame_2 = tk.Frame(main_frame, padx=5, pady=5, bd=3, relief=tk.GROOVE)
    frame_2.grid(row=0, column=1)

    tk.Label(frame_1, text="Torque in [Nm]:").grid(row=0, column=0)
    tk_torque_in = tk.Entry(frame_1)
    tk_torque_in.insert(0, torque_in)
    tk_torque_in.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(frame_1, text="rpm in [rpm]:").grid(row=1, column=0)
    tk_rpm_in = tk.Entry(frame_1)
    tk_rpm_in.insert(0, rpm_in)
    tk_rpm_in.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(frame_1, text="Torque out [Nm]:").grid(row=2, column=0)
    tk_torque_out = tk.Entry(frame_1)
    tk_torque_out.insert(0, torque_out)
    tk_torque_out.grid(row=2, column=1, padx=5, pady=5)

    tk.Label(frame_2, text="Hollow shaft external diameter [mm]:").grid(row=0, column=0)
    tk_diameter_hs = tk.Entry(frame_2)
    tk_diameter_hs.insert(0, diameter_hs)
    tk_diameter_hs.grid(row=0, column=1, padx=5, pady=5)

    tk.Label(frame_2, text="Dowel pin diameter [mm]:").grid(row=1, column=0)
    tk_diameter_axle = tk.Entry(frame_2)
    tk_diameter_axle.insert(0, diameter_axle)
    tk_diameter_axle.grid(row=1, column=1, padx=5, pady=5)

    tk.Label(frame_2, text='\u03941 [mm]:').grid(row=2, column=0)
    tk_delta_1 = tk.Entry(frame_2)
    tk_delta_1.insert(0, delta_1)
    tk_delta_1.grid(row=2, column=1, padx=5, pady=5)

    tk.Label(frame_2, text='\u03942 [mm]:').grid(row=3, column=0)
    tk_delta_2 = tk.Entry(frame_2)
    tk_delta_2.insert(0, delta_2)
    tk_delta_2.grid(row=3, column=1, padx=5, pady=5)

    font_run_button = tkFont.Font(family='Segoe UI', weight="bold", size=10)
    tk_run = tk.Button(frame_2, text="RUN", font=font_run_button, command=run, bg='sea green', fg='white')
    tk_run.grid(row=4, column=1, padx=10, pady=10)

    window.mainloop()

    return input_data

def create_gui_results(list_combinations_in):

    def update_interface():

        def update_display():
            nonlocal display_size_unscaled, display_size, canvas1

            canvas1.delete('all')
            diameters = [gearbox["Z1"] * gearbox["module_1"],
                         gearbox["Z2"] * gearbox["module_1"],
                         gearbox["Z3"] * gearbox["module_2"],
                         gearbox["Z4"] * gearbox["module_2"],
                         gearbox["Z5"] * gearbox["module_3"],
                         gearbox["Z6"] * gearbox["module_3"],
                         gearbox["diameter_hs"]]
            radius_unscaled = [round(diameter / 2) for diameter in diameters]

            # Defines the center of every gear axis, gears 2 and 3 share the same axis as they are assembled together.
            # Same holds for gears 4 and 5
            center_1_unscaled = {'x': display_size_unscaled['x'] / 2, 'y': display_size_unscaled['y'] * 0.95}
            center_2_unscaled = {'x': center_1_unscaled['x'],
                                 'y': center_1_unscaled['y'] - radius_unscaled[0] - radius_unscaled[1]}
            center_3_unscaled = {'x': center_1_unscaled['x'], 'y': center_2_unscaled['y']}
            center_4_unscaled = {'x': center_1_unscaled['x'],
                                 'y': center_3_unscaled['y'] - radius_unscaled[2] - radius_unscaled[3]}
            center_5_unscaled = {'x': center_1_unscaled['x'], 'y': center_4_unscaled['y']}
            center_6_unscaled = {'x': center_1_unscaled['x'],
                                 'y': center_5_unscaled['y'] - radius_unscaled[4] - radius_unscaled[5]}
            center_shaft_unscaled = {'x': center_1_unscaled['x'], 'y': center_6_unscaled['y']}

            # Scales the display size and the radius
            radius = [scale(r) for r in radius_unscaled]

            # Scales the position of every gear axis
            center_1 = {'x': scale(center_1_unscaled['x']), 'y': scale(center_1_unscaled['y'])}
            center_2 = {'x': scale(center_2_unscaled['x']), 'y': scale(center_2_unscaled['y'])}
            center_3 = {'x': scale(center_3_unscaled['x']), 'y': scale(center_3_unscaled['y'])}
            center_4 = {'x': scale(center_4_unscaled['x']), 'y': scale(center_4_unscaled['y'])}
            center_5 = {'x': scale(center_5_unscaled['x']), 'y': scale(center_5_unscaled['y'])}
            center_6 = {'x': scale(center_6_unscaled['x']), 'y': scale(center_6_unscaled['y'])}
            center_shaft = {'x': scale(center_shaft_unscaled['x']), 'y': scale(center_shaft_unscaled['y'])}

            # Defines the geometry of every circle
            oval_1 = {'x0': round(center_1['x'] - radius[0]),
                      'x1': round(center_1['x'] + radius[0]),
                      'y0': round(center_1['y'] - radius[0]),
                      'y1': round(center_1['y'] + radius[0])}
            oval_2 = {'x0': round(center_2['x'] - radius[1]),
                      'x1': round(center_2['x'] + radius[1]),
                      'y0': round(center_2['y'] - radius[1]),
                      'y1': round(center_2['y'] + radius[1])}
            oval_3 = {'x0': round(center_3['x'] - radius[2]),
                      'x1': round(center_3['x'] + radius[2]),
                      'y0': round(center_3['y'] - radius[2]),
                      'y1': round(center_3['y'] + radius[2])}
            oval_4 = {'x0': round(center_4['x'] - radius[3]),
                      'x1': round(center_4['x'] + radius[3]),
                      'y0': round(center_4['y'] - radius[3]),
                      'y1': round(center_4['y'] + radius[3])}
            oval_5 = {'x0': round(center_5['x'] - radius[4]),
                      'x1': round(center_5['x'] + radius[4]),
                      'y0': round(center_5['y'] - radius[4]),
                      'y1': round(center_5['y'] + radius[4])}
            oval_6 = {'x0': round(center_6['x'] - radius[5]),
                      'x1': round(center_6['x'] + radius[5]),
                      'y0': round(center_6['y'] - radius[5]),
                      'y1': round(center_6['y'] + radius[5])}
            oval_shaft = {'x0': round(center_shaft['x'] - radius[6]),
                          'x1': round(center_shaft['x'] + radius[6]),
                          'y0': round(center_shaft['y'] - radius[6]),
                          'y1': round(center_shaft['y'] + radius[6])}


            canvas1.create_oval(oval_1['x0'], oval_1['y0'], oval_1['x1'], oval_1['y1'], outline=colors[0], width=2)
            canvas1.create_oval(oval_2['x0'], oval_2['y0'], oval_2['x1'], oval_2['y1'], outline=colors[1], width=2)
            canvas1.create_oval(oval_3['x0'], oval_3['y0'], oval_3['x1'], oval_3['y1'], outline=colors[2], width=2)
            canvas1.create_oval(oval_4['x0'], oval_4['y0'], oval_4['x1'], oval_4['y1'], outline=colors[3], width=2)
            canvas1.create_oval(oval_5['x0'], oval_5['y0'], oval_5['x1'], oval_5['y1'], outline=colors[4], width=2)
            canvas1.create_oval(oval_6['x0'], oval_6['y0'], oval_6['x1'], oval_6['y1'], outline=colors[5], width=2)
            canvas1.create_oval(oval_shaft['x0'], oval_shaft['y0'], oval_shaft['x1'], oval_shaft['y1'],
                                outline=colors[6],
                                width=2)

            shift = 5
            canvas1.create_text(oval_1['x1'] + shift, oval_1['y1'] + shift,
                                text=f'D\u2081={str(round(diameters[0], 2))}mm', fill=colors[0])
            canvas1.create_text(oval_2['x1'] + shift, oval_2['y1'] + shift,
                                text=f'D\u2082={str(round(diameters[1], 2))}mm', fill=colors[1])
            canvas1.create_text(oval_3['x0'] - shift, oval_3['y1'] + shift,
                                text=f'D\u2083={str(round(diameters[2], 2))}mm', fill=colors[2])
            canvas1.create_text(oval_4['x1'] + shift, oval_4['y1'] + shift,
                                text=f'D\u2084={str(round(diameters[3], 2))}mm', fill=colors[3])
            canvas1.create_text(oval_5['x0'] - shift, oval_5['y1'] + shift,
                                text=f'D\u2085={str(round(diameters[4], 2))}mm', fill=colors[4])
            canvas1.create_text(oval_6['x1'] + shift, oval_6['y1'] + shift,
                                text=f'D\u2086={str(round(diameters[5], 2))}mm', fill=colors[5])
            canvas1.create_text(center_shaft['x'], center_shaft['y'],
                                text=f'Ds={str(round(diameters[6], 2))}mm', fill=colors[6])

            # Creates widgets for delta1
            canvas1.create_line(0, oval_2['y0'], display_size['x'], oval_2['y0'])
            canvas1.create_line(0, center_4['y'], display_size['x'], center_4['y'])
            canvas1.create_text(center_2['x'], round((oval_2['y0'] - center_4['y']) / 2 + center_4['y']),
                                text=f'\u0394\u2081 = {gearbox["delta1"]}mm')

            # Creates widgets for delta2
            canvas1.create_line(0, oval_4['y0'], display_size['x'], oval_4['y0'])
            canvas1.create_line(0, oval_shaft['y1'], display_size['x'], oval_shaft['y1'])
            canvas1.create_text(center_4['x'], round((oval_4['y0'] - oval_shaft['y1']) / 2 + oval_shaft['y1']),
                                text=f'\u0394\u2082 = {gearbox["delta2"]}mm')

            # Creates lines for gearbox-length
            canvas1.create_line(0, oval_1['y1'], display_size['x'], oval_1['y1'], width=2)
            canvas1.create_line(0, oval_6['y0'], display_size['x'], oval_6['y0'], width=2)
            canvas1.create_text(center_1['x'], oval_6['y0'] - 15, text=f'L={round(gearbox["gear_box_size"],2)}mm')

            return None

        nonlocal gearbox
        gearbox = list_combinations_in[gearbox_index]
        z1_r.delete(0, tk.END)
        z2_r.delete(0, tk.END)
        z3_r.delete(0, tk.END)
        z4_r.delete(0, tk.END)
        z5_r.delete(0, tk.END)
        z6_r.delete(0, tk.END)
        mod1_r.delete(0, tk.END)
        mod2_r.delete(0, tk.END)
        mod3_r.delete(0, tk.END)
        mod4_r.delete(0, tk.END)
        mod5_r.delete(0, tk.END)
        mod6_r.delete(0, tk.END)
        size_r.delete(0, tk.END)
        ratio_r.delete(0, tk.END)
        torque_r.delete(0, tk.END)
        rpm_r.delete(0, tk.END)
        delta1_r.delete(0, tk.END)
        delta2_r.delete(0, tk.END)

        z1_r.insert(0, str(gearbox["Z1"]))
        z2_r.insert(0, str(gearbox["Z2"]))
        z3_r.insert(0, str(gearbox["Z3"]))
        z4_r.insert(0, str(gearbox["Z4"]))
        z5_r.insert(0, str(gearbox["Z5"]))
        z6_r.insert(0, str(gearbox["Z6"]))
        mod1_r.insert(0, str(gearbox["module_1"]))
        mod2_r.insert(0, str(gearbox["module_1"]))
        mod3_r.insert(0, str(gearbox["module_2"]))
        mod4_r.insert(0, str(gearbox["module_2"]))
        mod5_r.insert(0, str(gearbox["module_3"]))
        mod6_r.insert(0, str(gearbox["module_3"]))
        size_r.insert(0, str(round(gearbox["gear_box_size"],2)))
        ratio_r.insert(0, str(round(gearbox["ratio"],2)))
        torque_r.insert(0, str(gearbox["torque_out"]))
        rpm_r.insert(0, str(gearbox["rpm_out"]))
        delta1_r.insert(0, str(gearbox["delta1"]))
        delta2_r.insert(0, str(gearbox["delta2"]))
        tk.Label(frame_0_r, text=f"Gearbox {gearbox_index + 1} ", font=custom_font).grid(row=1, column=0)
        update_display()

    def next_one():
        nonlocal gearbox_index
        if gearbox_index < len(list_combinations_in)-1:
            gearbox_index = gearbox_index + 1
        else:
            gearbox_index = 0
        update_interface()

    def previous_one():
        nonlocal gearbox_index
        if gearbox_index > 0:
            gearbox_index = gearbox_index - 1
        else:
            gearbox_index = len(list_combinations_in)-1
        update_interface()

    def scale(number):
        # Scales all dimensions to make everything fit into an 800 pixels long Display
        number = round(number*800/100)
        return number


    colors = [
        "#B85C5C",  # rojo
        "#C7A84B",  # amarillo
        "#7FA65A",  # verde
        "#9A668F",  # púrpura
        "#579B8A",  # turquesa
        "#C47A4A",  # naranja terracota
        "#5485A6",  # azul
    ]

    # Select gearbox
    # with open(r"C:\Users\aramirez\PycharmProjects/output.json", "r") as file:
    #     list_combinations_in = json.load(file)
    gearbox_index = 0
    gearbox = list_combinations_in[gearbox_index]

    display_size_unscaled = {'x': 35, 'y': 100}
    display_size = {'x': scale(display_size_unscaled['x']), 'y': scale(display_size_unscaled['y'])}

    window_r = tk.Tk()
    window_r.wm_title('3-Stage Gearbox Designer - Results')
    window_r.wm_iconbitmap('gear.ico')
    window_r.geometry("+%d+%d" %(100,100))


    # Creates frame structure
    main_frame = tk.Frame(window_r)
    main_frame_l = tk.Frame(main_frame, bd=3, relief=tk.GROOVE)
    main_frame_r = tk.Frame(main_frame, bd=3, relief=tk.GROOVE)
    frame_0_r = tk.Frame(main_frame_l, padx=5, pady=5)
    frame_1_r = tk.Frame(main_frame_l, padx=5, pady=5, bd=1, relief=tk.GROOVE)
    frame_1_r_bot_l = tk.Frame(frame_1_r, padx=5, pady=5)
    frame_1_r_bot_r = tk.Frame(frame_1_r, padx=5, pady=5)
    frame_2_r = tk.Frame(main_frame_l, padx=5, pady=5, bd=1, relief=tk.GROOVE)
    frame_3_r = tk.Frame(main_frame_l, padx=5, pady=5, bd=1, relief=tk.GROOVE)
    frame_4_r = tk.Frame(main_frame_l, padx=5, pady=5)
    # Positions frame structure
    main_frame.grid(row=0, column=0)
    main_frame_l.grid(row=0, column=0, padx=5, pady=5)
    main_frame_r.grid(row=0, column=1, padx=5, pady=5)
    frame_0_r.grid(row=0, column=0, padx=5, pady=5)
    frame_1_r.grid(row=1, column=0, padx=5, pady=5)
    frame_1_r_bot_l.grid(row=1, column=0, padx=5, pady=5)
    frame_1_r_bot_r.grid(row=1, column=1, padx=5, pady=5)
    frame_2_r.grid(row=2, column=0, padx=5, pady=5)
    frame_3_r.grid(row=3, column=0, padx=5, pady=5)
    frame_4_r.grid(row=4, column=0, padx=5, pady=5)

    # Creates Labels
    custom_font = tkFont.Font(size=12)
    tk.Label(frame_0_r, text=f"Eligible Gearboxes = {len(list_combinations_in)} ", font=custom_font).grid(row=0, column=0)
    tk.Label(frame_0_r, text=f"Gearbox {gearbox_index + 1} ", font=custom_font).grid(row=1, column=0)
    tk.Label(frame_1_r, text="Number of teeth:").grid(row=0, column=0)
    tk.Label(frame_1_r, text="Module:").grid(row=0, column=1)
    tk.Label(frame_1_r_bot_l, text="Z\u2081 :").grid(row=0, column=0)
    tk.Label(frame_1_r_bot_l, text="Z\u2082 :").grid(row=1, column=0)
    tk.Label(frame_1_r_bot_l, text="Z\u2083 :").grid(row=2, column=0)
    tk.Label(frame_1_r_bot_l, text="Z\u2084 :").grid(row=3, column=0)
    tk.Label(frame_1_r_bot_l, text="Z\u2085 :").grid(row=4, column=0)
    tk.Label(frame_1_r_bot_l, text="Z\u2086 :").grid(row=5, column=0)
    # Creates the Entry fields to display the information
    z1_r = tk.Entry(frame_1_r_bot_l)
    z2_r = tk.Entry(frame_1_r_bot_l)
    z3_r = tk.Entry(frame_1_r_bot_l)
    z4_r = tk.Entry(frame_1_r_bot_l)
    z5_r = tk.Entry(frame_1_r_bot_l)
    z6_r = tk.Entry(frame_1_r_bot_l)
    z1_r.grid(row=0, column=1, padx=5, pady=5)
    z2_r.grid(row=1, column=1, padx=5, pady=5)
    z3_r.grid(row=2, column=1, padx=5, pady=5)
    z4_r.grid(row=3, column=1, padx=5, pady=5)
    z5_r.grid(row=4, column=1, padx=5, pady=5)
    z6_r.grid(row=5, column=1, padx=5, pady=5)

    # Creates Labels for the modules
    tk.Label(frame_1_r_bot_r, text="m\u2081 :").grid(row=0, column=2)
    tk.Label(frame_1_r_bot_r, text="m\u2082 :").grid(row=1, column=2)
    tk.Label(frame_1_r_bot_r, text="m\u2083 :").grid(row=2, column=2)
    tk.Label(frame_1_r_bot_r, text="m\u2084 :").grid(row=3, column=2)
    tk.Label(frame_1_r_bot_r, text="m\u2085 :").grid(row=4, column=2)
    tk.Label(frame_1_r_bot_r, text="m\u2086 :").grid(row=5, column=2)

    # Creates the Entry fields for the Modules
    mod1_r = tk.Entry(frame_1_r_bot_r)
    mod2_r = tk.Entry(frame_1_r_bot_r)
    mod3_r = tk.Entry(frame_1_r_bot_r)
    mod4_r = tk.Entry(frame_1_r_bot_r)
    mod5_r = tk.Entry(frame_1_r_bot_r)
    mod6_r = tk.Entry(frame_1_r_bot_r)
    mod1_r.grid(row=0, column=3, padx=5, pady=5)
    mod2_r.grid(row=1, column=3, padx=5, pady=5)
    mod3_r.grid(row=2, column=3, padx=5, pady=5)
    mod4_r.grid(row=3, column=3, padx=5, pady=5)
    mod5_r.grid(row=4, column=3, padx=5, pady=5)
    mod6_r.grid(row=5, column=3, padx=5, pady=5)

    # Frame 2
    tk.Label(frame_2_r, text="\u0394\u2081 :").grid(row=3, column=0)
    tk.Label(frame_2_r, text="\u0394\u2082 :").grid(row=4, column=0)
    delta1_r = tk.Entry(frame_2_r)
    delta2_r = tk.Entry(frame_2_r)
    delta1_r.grid(row=3, column=1, padx=5, pady=5)
    delta2_r.grid(row=4, column=1, padx=5, pady=5)

    # Frame 3
    tk.Label(frame_3_r, text="Gear Ratio :").grid(row=0, column=0)
    tk.Label(frame_3_r, text="Output Torque :").grid(row=1, column=0)
    tk.Label(frame_3_r, text="Output RPM :").grid(row=2, column=0)
    tk.Label(frame_3_r, text="Gearbox size :").grid(row=3, column=0)
    ratio_r = tk.Entry(frame_3_r)
    torque_r = tk.Entry(frame_3_r)
    rpm_r = tk.Entry(frame_3_r)
    size_r = tk.Entry(frame_3_r)
    ratio_r.grid(row=0, column=1, padx=5, pady=5)
    torque_r.grid(row=1, column=1, padx=5, pady=5)
    rpm_r.grid(row=2, column=1, padx=5, pady=5)
    size_r.grid(row=3, column=1, padx=5, pady=5)

    # Frame 4
    custom_font_2 = tkFont.Font(family='Segoe UI', weight="bold", size=9)
    prev_r = tk.Button(frame_4_r, text="< Prev", font=custom_font_2, command=lambda: previous_one(), background="medium sea green", fg="white")
    next_r = tk.Button(frame_4_r, text="Next >", font=custom_font_2, command=lambda: next_one(),  background="medium sea green", fg="white")
    prev_r.grid(row=0, column=0, padx=5, pady=5)
    next_r.grid(row=0, column=1, padx=5, pady=5)

    canvas1 = tk.Canvas(main_frame_r, width=display_size['x'], height=display_size['y'], background="white")
    canvas1.grid(row=0, column=0)

    update_interface()

    window_r.mainloop()

if __name__ == '__main__':
    list_combinations = []
    ################################################
    input_data = create_gui_1()
    list_combinations = get_best_modules(input_data)
    list_combinations.sort(key=lambda x: x['gear_box_size'])
    print('Fullfill requirements = ', len(list_combinations))
    with open(r"C:\Users\aramirez\PycharmProjects/output.json", "w") as file:
        json.dump(list_combinations, file, indent=4)  # indent for pretty-printing
    if len(list_combinations):
        pprint(list_combinations[len(list_combinations)-1])

    create_gui_results(list_combinations)
