# imports
from opentrons import containers, instruments, robot

# containers
trash = containers.load('point', 'E2')
plate = containers.load('96-flat', 'B1')
samples = containers.load('96-flat', 'C1')  # Load this later?

t10 = containers.load('tiprack-10ul', 'A1')

# pipettes
p20 = instruments.Pipette(axis='b',
                          max_volume=20,
                          tip_racks=[t10],
                          trash_container=trash)

# Transfer 15ul of mastermix to all 96 wells on the plate
mastermix = containers.load('tube-rack-2ml', 'A2')

def main(tip_start_col='A', mix_loc='A1'):

    # Step 1. Load the mastermix
    p20.start_at_tip(t10[tip_start_col])
    current_row = 0

    # run this loop once for each row
    for tip in t10.cols(tip_start_col):
        p20.pick_up_tip(tip)

        for well in samples.rows(current_row):
            p20.move_to(mastermix[mix_loc])
            p20.mix(2, 7.5)
            p20.aspirate(7.5, mastermix.wells(mix_loc))
            p20.dispense(well)
            # p20.transfer(10, mastermix.wells(mix_loc), plate.wells(well))
        current_row += 1
        # trash our tip to associated trash container
        p20.drop_tip()
    # Step 2. Load our sample.
    p20.delay()

    for c in robot.commands():
        print(c)
if __name__ == '__main__':
    main(tip_start_col='B')
