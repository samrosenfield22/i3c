

#ifndef I3C_CONFIG_H_
#define I3C_CONFIG_H_

//number of registers that are scanned for each device. default is 256.
#define MAX_REGISTERS (256)

/* if the electrical test determines that the i2c bus is using 3V3 logic, the user is prompted to confirm that this is what they want. to skip this (i.e. if you
 *  know that the device is 3V3-tolerant, this prompt would be annoying), comment out the definition. */
#define WARN_FOR_3V3_LOGIC

//each register is read multiple times; if the value changed, the register is marked as "unstable". this determines the number of scans.
#define REGISTER_SCAN_CT (5)

//duration (in milliseconds) to delay between each register scan
#define REGISTER_SCAN_DELAY (100)


#endif //I3C_CONFIG_H_
