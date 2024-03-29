# imports
from opentrons import containers, instruments, robot

# containers
containers.create(
    'tiprack-100ul',
    grid=(8, 12),
    spacing=(12, 12),
    diameter=3.5,
    depth=60
)

trash = containers.load('point', 'E2')
plate = containers.load('96-PCR-tall', 'B1')
samples = containers.load('96-flat', 'C1')
mastermix = containers.load('tube-rack-2ml', 'A2')

t10 = containers.load('tiprack-10ul', 'A1')
t100 = containers.load('tiprack-20ul', 'A3')

# pipettes
p100 = instruments.Pipette(axis='b',
                           max_volume=100,
                           tip_racks=[t10],
                           trash_container=trash)
p50 = instruments.Pipette(axis='a',
                          max_volume=50,
                          tip_racks=[t10],
                          trash_container=trash,
                          channels=8)


def print_history():
    for c in robot.commands():
        print(c)


def main(tip_start_col='A', mix_loc='A1', sample_range=list(range(1, 11)), sybr_only=[0, 11]):
    # Step 1. Load the mastermix

    # Which column should the robot take tips from?
    tip_column = t100[tip_start_col]
    # Location of Sybr green tube in our tube rack (A1 by default)
    sybr_pos = mastermix[mix_loc]
    p100.start_at_tip(tip_column)
    current_row = 0

    # run this loop once for each tip in the column, taking tips from A1...A12
    for tip in t100.cols(tip_start_col):
        # Only fill this row if it's found in our samples_range or sybr_only lists
        if current_row in (sample_range + sybr_only):
            p100.pick_up_tip(tip)
            # This loop runs once for every well in the current row of our destination plate, going from A1...H1
            for well in plate.rows(current_row):
                # This is to make sure the column we're putting sybr green into will also have a sample later on
                p100.move_to(sybr_pos)
                # Fill the tip to the maximum volume
                empty_volume = 100 - p100.current_volume
                # We start out by priming the tip with our Sybr Green solution
                p100.mix(2, empty_volume)
                # This ensures that the tip is always at capacity.
                p100.aspirate(empty_volume, sybr_pos)
                # .bottom(3) specifies that dispensing should occur 3mm from the bottom of the well
                p100.dispense(15, well.bottom(3))

            p100.dispense(p100.current_volume, sybr_pos)
            p100.blow_out()
            p100.drop_tip()
        current_row += 1

    # Use robot.pause() if using the API through a custom environment (i.e. Jupyter)
    # robot.pause()
    # Sybr green should be refrigerated and samples set on C1
    p100.delay(minutes=15)
    # robot.clear_commands() # clear_commands for isolating the later parts of a run

    # Step 2. Load our sample

    # Here we iterate by row (i.e.: A1...H1) and transfer 5uL x6 of sample to our destination plate w/ Sybr green
    for tip_row, sample_row, dest_row in zip(t10.rows(sample_range), samples.rows(sample_range),
                                             plate.rows(sample_range)):
        p50.pick_up_tip(tip_row)
        p50.aspirate(5, sample_row)
        p50.dispense(dest_row)
        # Drops the tip in the trash since the p50 is associated with it
        p50.drop_tip()


if __name__ == '__main__':
    # Use tip_start_col to define which column should be used from the 10uL tips
    main(tip_start_col='B', mix_loc='A1', sample_range=[1, 2, 3, 4, 5, 6, 7, 8, 9, 10], sybr_only=[0, 11])
    print_history()
