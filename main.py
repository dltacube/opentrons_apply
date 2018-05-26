# imports
from opentrons import containers, instruments, robot

# containers
containers.create(
    'tiprack-20ul',
    grid=(8, 12),
    spacing=(12, 12),
    diameter=5,
    depth=10
)

trash = containers.load('point', 'E2')
plate = containers.load('96-flat', 'B1')
samples = containers.load('96-flat', 'C1')  # Load this later?

t10 = containers.load('tiprack-10ul', 'A1')
t20 = containers.load('tiprack-20ul', 'A3')

# pipettes
p20 = instruments.Pipette(axis='b',
                          max_volume=20,
                          tip_racks=[t10],
                          trash_container=trash)
p50 = instruments.Pipette(axis='a',
                          max_volume=50,
                          tip_racks=[t10],
                          trash_container=trash,
                          channels=8)

# Transfer 15ul of mastermix to all 96 wells on the plate
mastermix = containers.load('tube-rack-2ml', 'A2')


def main(tip_start_col='A', mix_loc='A1', sample_range=list(range(1, 11))):
    # Step 1. Load the mastermix
    # Which column should the robot take tips from?
    tip_column = t20[tip_start_col]
    # Location of Sybr green tube in our tube rack (A1 by default)
    sybr_pos = mastermix[mix_loc]
    p20.start_at_tip(tip_column)
    current_row = 0

    # run this loop once for each tip in the column, taking tips from A1...A12
    for tip in t20.cols(tip_start_col):
        p20.pick_up_tip(tip)

        # This loop runs once for every well in the current row of our destination plate, going from A1...H1
        for well in plate.rows(current_row):
            p20.move_to(sybr_pos)
            # We start out by priming the tip with our Sybr Green solution
            p20.mix(2, 15)
            p20.aspirate(15, sybr_pos)
            p20.dispense(well)

        current_row += 1
        p20.drop_tip()
    p20.delay(minutes=15)

    # Step 2. Load our sample.
    # Here we iterate by row (i.e.: A1...H1) and transfer 5uL x8 of sample to our destination plate w/ Sybr green
    for tip_row, sample_row, dest_row in zip(t10.rows, samples.rows(sample_range), plate.rows(1, to=10)):
        p50.pick_up_tip(tip_row)
        p50.aspirate(5, samples.rows(sample_range))
        p50.dispense(plate.rows(sample_range))
        # Drops the tip in the trash since the p50 is associated with it
        p50.drop_tip()

    for c in robot.commands():
        print(c)


if __name__ == '__main__':
    # Use tip_start_col to define which column should be used from the 10uL tips
    main(tip_start_col='B', sample_range=[0, 2, 3, 4, 6, 7, 8, 9, 10, 11])
