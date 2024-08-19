# -*- coding: utf-8 -*-
"""This file is part of the libsigrokdecode project.

Copyright (C) 2019 Libor Gabaj <libor.gabaj@gmail.com>

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, see <http://www.gnu.org/licenses/>.

"""

import sigrokdecode as srd


"""
OUTPUT_PYTHON format:

Packet:
[<ptype>, <pdata>]

<ptype>:
 - "START" (START condition)
 - "COMMAND" (Command)
 - "DATA" (Data)
 - "STOP" (STOP condition)
 - "ACK" (ACK bit)
 - "NACK" (NACK bit)
 - "BITS" (<pdata>: list of data bits and their ss/es numbers)

<pdata> is the data byte associated with the "DATA*" command.
For "START", "STOP", "ACK", and "NACK" <pdata> is None.
"""
###############################################################################
# Channels
###############################################################################
CLK = 0     # Serial clock
DIO = 1     # Data input/output
STB = 2     # Strobe line


###############################################################################
# Enumeration classes for device parameters
###############################################################################
class Bus:
    """Enumeration of possible driver chip types."""

    (WIRE2, WIRE3) = (0, 1)


###############################################################################
# Enumeration classes for annotations
###############################################################################
class AnnProtocol:
    """Enumeration of annotations for protocol states."""

    (START, STOP, ACK, NACK, COMMAND, DATA, BIT) = range(7)


class AnnInfo:
    """Enumeration of annotations for formatted info."""

    (WARN,) = (AnnProtocol.BIT + 1,)


class AnnBinary:
    """Enumeration of annotations for binary info."""

    (DATA,) = (0,)


###############################################################################
# Parameters mapping
###############################################################################
commands = {
    AnnProtocol.START: "START",
    AnnProtocol.STOP: "STOP",
    AnnProtocol.ACK: "ACK",
    AnnProtocol.NACK: "NACK",
    AnnProtocol.COMMAND: "COMMAND",
    AnnProtocol.DATA: "DATA",
    AnnProtocol.BIT: "BITS",
}


###############################################################################
# Parameters anotations definitions
###############################################################################
"""
- The last item of an annotation list is used repeatedly without a value.
- The last two items of an annotation list are used repeatedly without a value.
"""
protocol = {
    AnnProtocol.START: ["Start", "S"],
    AnnProtocol.STOP: ["Stop", "P"],
    AnnProtocol.ACK: ["ACK", "A"],
    AnnProtocol.NACK: ["NACK", "N"],
    AnnProtocol.COMMAND: ["Command", "Cmd", "C"],
    AnnProtocol.DATA: ["Data", "D"],
    AnnProtocol.BIT: ["Bit", "B"],
}

info = {
    AnnInfo.WARN: ["Warnings", "Warn", "W"],
}

binary = {
    AnnBinary.DATA: ["Data", "D"],
}


###############################################################################
# Helpers
###############################################################################
def format_data(data, radix="Hex"):
    """Format data value according to the radix option."""
    radix = radix.upper()
    if radix == "DEC":
        format = "{:#d}"
    elif radix == "BIN":
        format = "{:#b}"
    elif radix == "OCT":
        format = "{:#o}"
    else:
        format = "{:#04x}"
    return format.format(data)


def create_annots(annots_dict):
    """Create a tuple with all annotation definitions dictionary.

    Arguments
    ---------
    annots_dict : dictionary
        Dictionary of annotation definitions in the scheme {prefix: def_dict},
        where:
        prefix : string
            Key of the annotation dictionary as a prefix of the annotation
            name in the Decoder class. It is going to be appended with numeric
            key from the value of the annotation dictionary.
        def_dict : dictionary
            Value of the annotation dictioniary, which is again a dictionary
            defining particular set of annotations.
            - The key of the dictionary is the index of the definition, which
              is an attribute of corresponding annotation class defined in the
              Decoder module outside the Decoder class.
            - The vallue of the dictionary is the list of annotation strings,
              usually from the longest to the shortest.

    Returns
    -------
    tuple of str
        Annotations definitions compliant with Protocol Decoder API.

    """
    annots = []
    for prefix, ann_def in annots_dict.items():
        for ann_idx, ann_list in ann_def.items():
            annots.insert(ann_idx, tuple([prefix + "-" + ann_list[0].lower(),
                                         ann_list[0]]))
    return tuple(annots)


def compose_annot(ann_label="", ann_value=None, ann_unit=None,
                  ann_action=None):
    """Compose list of annotations enriched with value and unit.

    Arguments
    ---------
    ann_label : list
        List of annotation labels for enriching with values and units and
        prefixed with actions.
        If label is none or empty string, there is used neither it nor its
        delimiter, just other arguments, if any.
    ann_value : list
        List of values to be added item by item to all annotations.
    ann_unit : list
        List of measurement units to be added item by item to all
        annotations. The method does not add separation space between
        the value and the unit.
    ann_action : list
        List of action prefixes prepend item by item to all annotations.
        The method separates action and annotation with a space.

    Returns
    -------
    list of str
        List of a annotations potentially enriched with values and units
        with items sorted by length descending.

    Notes
    -----
    - Usually just one value and one unit is used. However for flexibility
      more of them can be used.
    - If the annotation values list is not defined, the annotation units
      list is not used, even if it is defined.

    """
    if ann_label is None:
        ann_label = ""
    if not isinstance(ann_label, list):
        tmp = ann_label
        ann_label = []
        ann_label.append(tmp)

    if ann_value is None:
        ann_value = []
    elif not isinstance(ann_value, list):
        tmp = ann_value
        ann_value = []
        ann_value.append(tmp)

    if ann_unit is None:
        ann_unit = []
    elif not isinstance(ann_unit, list):
        tmp = ann_unit
        ann_unit = []
        ann_unit.append(tmp)

    if ann_action is None:
        ann_action = []
    elif not isinstance(ann_action, list):
        tmp = ann_action
        ann_action = []
        ann_action.append(tmp)
    if len(ann_action) == 0:
        ann_action = [""]

    # Compose annotation
    annots = []
    for act in ann_action:
        for lbl in ann_label:
            ann = "{} {}".format(act, lbl).strip()
            ann_item = None
            for val in ann_value:
                if len(ann) > 0:
                    ann_item = "{}: {}".format(ann, val)
                else:
                    ann_item = "{}".format(val)
                annots.append(ann_item)  # Without units
                for unit in ann_unit:
                    ann_item += "{}".format(unit)
                    annots.append(ann_item)  # With units
            if ann_item is None:
                annots.append(ann)

    # Add last 2 annotation items without values
    if len(ann_value) > 0:
        for ann in ann_label[-2:]:
            if len(ann) > 0:
                annots.append(ann)
    annots.sort(key=len, reverse=True)
    return annots


###############################################################################
# Decoder
###############################################################################
class SamplerateError(Exception):
    """Custom exception."""

    pass


class ChannelError(Exception):
    """Custom exception."""

    pass


class Decoder(srd.Decoder):
    """Protocol decoder for Titan Micro Circuits."""

    api_version = 3
    id = "tmc"
    name = "TMC"
    longname = "Titan Micro Circuit"
    desc = "Bus for TM1636/37/38 7-segment digital tubes."
    license = "gplv2+"
    inputs = ["logic"]
    outputs = ["tmc"]
    channels = (
        {"id": "clk", "name": "CLK", "desc": "Clock line"},
        {"id": "dio", "name": "DIO", "desc": "Data line"},
    )
    optional_channels = (
        {"id": "stb", "name": "STB", "desc": "Strobe line"},
    )
    options = (
        {"id": "radix", "desc": "Number format", "default": "Hex",
         "values": ("Hex", "Dec", "Oct", "Bin")},
    )
    annotations = create_annots(
        {
            "prot": protocol,
            "info": info,
         }
    )
    annotation_rows = (
        ("bits", "Bits", (AnnProtocol.BIT,)),
        ("data", "Cmd/Data", tuple(range(
            AnnProtocol.START, AnnProtocol.DATA + 1
            ))),
        ("warnings", "Warnings", (AnnInfo.WARN,)),
    )
    binary = create_annots({"data": binary})

    def __init__(self):
        """Initialize decoder."""
        self.reset()

    def reset(self):
        """Reset decoder and initialize instance variables."""
        self.ss = self.es = self.ss_byte = self.ss_ack = -1
        self.samplerate = None
        self.pdu_start = None
        self.pdu_bits = 0
        self.bustype = None
        self.bytecount = 0
        self.clear_data()
        self.state = "FIND START"

    def metadata(self, key, value):
        """Pass metadata about the data stream."""
        if key == srd.SRD_CONF_SAMPLERATE:
            self.samplerate = value

    def start(self):
        """Actions before the beginning of the decoding."""
        self.out_python = self.register(srd.OUTPUT_PYTHON)
        self.out_ann = self.register(srd.OUTPUT_ANN)
        self.out_binary = self.register(srd.OUTPUT_BINARY)
        self.out_bitrate = self.register(
            srd.OUTPUT_META,
            meta=(int, "Bitrate", "Bitrate from Start bit to Stop bit")
        )

    def putx(self, data):
        """Show data to annotation output across bit range."""
        self.put(self.ss, self.es, self.out_ann, data)

    def putp(self, data):
        """Show data to python output across bit range."""
        self.put(self.ss, self.es, self.out_python, data)

    def putb(self, data):
        """Show data to binary output across bit range."""
        self.put(self.ss, self.es, self.out_binary, data)

    def clear_data(self):
        """Clear data cache."""
        self.bitcount = 0
        self.databyte = 0
        self.bits = []

    def handle_bitrate(self):
        """Calculate bitrate."""
        elapsed = 1 / float(self.samplerate)    # Sample time period
        elapsed *= self.samplenum - self.pdu_start - 1
        if elapsed:
            bitrate = int(1 / elapsed * self.pdu_bits)
            self.put(self.ss_byte, self.samplenum, self.out_bitrate, bitrate)

    def handle_start(self, pins):
        """Process start condition."""
        self.ss, self.es = self.samplenum, self.samplenum
        self.pdu_start = self.samplenum
        self.pdu_bits = 0
        self.bytecount = 0
        cmd = AnnProtocol.START
        self.putp([commands[cmd], None])
        self.putx([cmd, protocol[cmd]])
        self.clear_data()
        self.state = "FIND DATA"

    def handle_data(self, pins):
        """Create name and call corresponding data handler."""
        self.pdu_bits += 1
        if self.bitcount == 0:
            self.ss_byte = self.samplenum
        fn = getattr(self, "handle_data_{}".format(self.bustype))
        fn(pins)

    def handle_stop(self):
        """Create name and call corresponding stop handler."""
        fn = getattr(self, "handle_stop_{}".format(self.bustype))
        fn()

    def handle_data_wire2(self, pins):
        """Process data bits for 2-wire bus.

        Arguments
        ---------
        pins : tuple
            Tuple of bit values (0 or 1) for each channel from the first one.

        Notes
        -----
        - The method is called at rising edge of each clock pulse regardless of
          its purpose or meaning.
        - For acknowledge clock pulse and start/stop pulse the registration of
          this bit is provided in vain just for simplicity of the method.
        - The method stores individual bits and their start/end sample numbers.
        - In the bit list, index 0 represents the recently processed bit, which
          is finally the MSB (LSB-first transmission).
        - The method displays previous bit because its end sample number is
          known just at processing the current bit.

        """
        clk, dio, stb = pins
        self.bits.insert(0, [dio, self.samplenum, self.samplenum])
        # Register end sample of the previous bit and display it
        if self.bitcount > 0:
            self.bits[1][2] = self.samplenum
            # Display previous data bit
            if self.bitcount <= 8:
                annots = [str(self.bits[1][0])]
                self.put(self.bits[1][1], self.bits[1][2], self.out_ann,
                         [AnnProtocol.BIT, annots])
        # Include current data bit to data byte (LSB-first transmission)
        self.bitcount += 1
        if self.bitcount <= 8:
            self.databyte >>= 1
            self.databyte |= (dio << 7)
            return
        # Display data byte
        self.ss, self.es = self.ss_byte, self.samplenum
        cmd = (AnnProtocol.DATA, AnnProtocol.COMMAND)[self.bytecount == 0]
        self.bits = self.bits[-8:]    # Remove superfluous bits (ACK)
        self.bits.reverse()
        self.putp([commands[AnnProtocol.BIT], self.bits])
        self.putp([commands[cmd], self.databyte])
        self.putb([AnnBinary.DATA, bytes([self.databyte])])
        annots = compose_annot(
            protocol[cmd],
            ann_value=format_data(self.databyte, self.options["radix"])
        )
        self.putx([cmd, annots])
        self.clear_data()
        self.ss_ack = self.samplenum  # Remember start of ACK bit
        self.bytecount += 1
        self.state = "FIND ACK"

    def handle_ack(self, pins):
        """Process ACK/NACK bit."""
        clk, dio, stb = pins
        self.ss, self.es = self.ss_ack, self.samplenum
        cmd = (AnnProtocol.ACK, AnnProtocol.NACK)[dio]
        self.putp([commands[cmd], None])
        self.putx([cmd, protocol[cmd]])
        self.state = "FIND DATA"

    def handle_stop_wire2(self):
        """Process stop condition for 2-wire bus."""
        self.handle_bitrate()
        # Display stop
        cmd = AnnProtocol.STOP
        self.ss, self.es = self.samplenum, self.samplenum
        self.putp([commands[cmd], None])
        self.putx([cmd, protocol[cmd]])
        self.clear_data()
        self.state = "FIND START"

    def handle_byte_wire3(self):
        """Process data byte after last CLK pulse for 3-wire bus."""
        if not self.bits:
            return
        # Display all bits
        self.bits[0][2] = self.samplenum    # Update end sample of the last bit
        for bit in self.bits:
            annots = [str(bit[0])]
            self.put(bit[1], bit[2], self.out_ann, [AnnProtocol.BIT, annots])
        # Display data byte
        self.ss, self.es = self.ss_byte, self.samplenum
        cmd = (AnnProtocol.DATA, AnnProtocol.COMMAND)[self.bytecount == 0]
        self.bits.reverse()
        self.putp([commands[AnnProtocol.BIT], self.bits])
        self.putp([commands[cmd], self.databyte])
        self.putb([AnnBinary.DATA, bytes([self.databyte])])
        annots = compose_annot(
            protocol[cmd],
            ann_value=format_data(self.databyte, self.options["radix"])
        )
        self.putx([cmd, annots])
        self.bytecount += 1

    def handle_data_wire3(self, pins):
        """Process data bits at CLK rising edge for 3-wire bus."""
        clk, dio, stb = pins
        if self.bitcount >= 8:
            self.handle_byte_wire3()
            self.clear_data()
            self.ss_byte = self.samplenum
        self.bits.insert(0, [dio, self.samplenum, self.samplenum])
        self.databyte >>= 1
        self.databyte |= (dio << 7)
        # Register end sample of the previous bit
        if self.bitcount > 0:
            self.bits[1][2] = self.samplenum
        self.bitcount += 1

    def handle_stop_wire3(self):
        """Process stop condition for 3-wire bus."""
        self.handle_bitrate()
        self.handle_byte_wire3()
        # Display stop
        cmd = AnnProtocol.STOP
        self.ss, self.es = self.samplenum, self.samplenum
        self.putp([commands[cmd], None])
        self.putx([cmd, protocol[cmd]])
        self.clear_data()
        self.state = "FIND START"

    def decode(self):
        """Decode samples provided by logic analyzer."""
        if not self.samplerate:
            raise SamplerateError("Cannot decode without samplerate.")
        has_pin = [self.has_channel(ch) for ch in (CLK, DIO)]
        if has_pin != [True, True]:
            raise ChannelError("Both CLK and DIO pins required.")
        while True:
            # State machine
            if self.state == "FIND START":
                # Wait for any of the START conditions:
                # WIRE3: CLK = high, STB = falling
                # WIRE2: CLK = high, DIO = falling
                pins = self.wait([
                    {CLK: 'h', STB: "f"},
                    {CLK: 'l', STB: "f"},
                    {CLK: "h", DIO: "f"},
                ])
                if self.matched[0] or self.matched[1]:
                    self.bustype = "wire3"
                    self.handle_start(pins)
                elif self.matched[2]:
                        self.bustype = "wire2"
                        self.handle_start(pins)
            elif self.state == "FIND DATA":
                # Wait for any of the following conditions:
                #  WIRE3 STOP condition: STB = rising
                #  WIRE2 STOP condition: CLK = high, DIO = rising
                #  Clock pulse: CLK = rising
                pins = self.wait([
                    {STB: "r"},
                    {CLK: "h", DIO: "r"},
                    {CLK: "r"},
                ])
                if self.matched[0] or self.matched[1]:
                    self.handle_stop()
                elif self.matched[2]:
                    self.handle_data(pins)
            elif self.state == "FIND ACK":
                # Wait for an ACK bit
                self.handle_ack(self.wait({CLK: "f"}))
            elif self.state == "FIND STOP":
                # Wait for STOP conditions:
                #  WIRE3 STOP condition: STB = rising
                #  WIRE2 STOP condition: CLK = high, DIO = rising
                pins = self.wait([
                    {STB: "r"},
                    {CLK: "h", DIO: "r"},
                ])
                if self.matched[0] or self.matched[1]:
                    self.handle_stop()
