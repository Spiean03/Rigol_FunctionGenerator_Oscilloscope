# -*- coding: utf-8 -*-
"""
Created on Thu Mar 09 12:56:14 2017

@author: aspiel
"""

from instruments import *
import time
import numpy as np
import matplotlib.pyplot as plt

def characterize (vector):
    "This will return 4 parameters: amp, period(in samples), phase(in samples),crossing_count"
    debug = 0 # make this non-zero to enable printing out debugging statements
    max = vector.max()
    min = vector.min()
    length = vector.size
    amp = 0.5 * (max - min)
    zero = 0.5 * (min + max) # threshold used for zero crossings
    half_max = 0.5 * (max + zero) # these are trip points which re-arm zero crossing detection
    half_min = 0.5 * (min + zero)
    side = vector[0] > zero # this is logic true is current sample is above zero
    armed = 1    # zero crossing will be detected if this is logic true
    crossing_count = 0 # number of zero crossings detected
    rising = []   # lists of sample indexes where zero-crossings detected
    falling = []
    crossing = []
    for i in range(length) :
        if armed :
            if side and vector[i] < zero :
                armed = 0 # deactivate zero crossing until reach half_min
                falling.append(i)
                crossing.append(i)
                crossing_count = crossing_count + 1
                side = 0
                if debug : print "falling zero crossing at %d" % (i)
            if not side and vector[i] > zero :
                armed = 0 # deactivate zero crossing until reach half_max
                rising.append(i)
                crossing.append(i)
                crossing_count = crossing_count + 1
                side = 1
                if debug : print "rising zero crossing at %d" % (i)
        else :
            if (side and vector[i] > half_max) or (not side and vector[i] < half_min) :
                armed = 1
                
    if debug :print "crossing_count = %d" % crossing_count
    if crossing_count < 4 :
        print "crossing_count too low"
        return (0,0,0,crossing_count)
    half_periods = np.array(crossing[1:]) - np.array(crossing[:-1])
    period = 2*half_periods.mean()
    if debug : print "period = %f" % (period)
    crossing_indexes = range(crossing_count)
    phase_delays = np.array(crossing) - np.array(crossing_indexes)*period/2
    phase_delay = phase_delays.mean()
    if rising[0] > falling[0] : # if first zero crossing is falling, first rising is period/2 later
        phase_delay = phase_delay + period / 2
    if debug : print "phase_delay = %f" % phase_delay
    return (amp, period, phase_delay, crossing_count)

def bode (frequencies, amplitude=1,delay=0.01) :
    # Initialize instruments
    gen = Generator()
    scope = Scope()
    # Record vertical gain settings
    x_gain = scope.getVerticalGain(1) # volts / division
    y_gain = scope.getVerticalGain(2)
    # setup plotting window
    f,(signal_plot,phase_plot,mag_plot) = plt.subplots(3)
    signal_plot.set_xlabel("Time (s)")
    signal_plot.set_ylabel("Sample values")
    freq_range = [frequencies.min(),frequencies.max()]
    mag_plot.set_xlim(freq_range)
    phase_plot.set_xlim(freq_range)
    mag_plot.set_xlabel("Frequency (Hz)")
    phase_plot.set_ylabel("Phase (radians)")
    mag_plot.set_ylabel("Gain")
    plt.ion()

    gains = []  # create emply lists for values to be returned
    phases = []
    for i in range(frequencies.size):
        frequency = frequencies[i]
        period = 1.0 / frequency
        gen.sine(1,frequency,amplitude) # generate signal on channel 1
        timebase = scope.setTimebase(5*period/12) # shoot for 5 cycles, there are 12 divisions
        plt.pause(0.01) # let circuit settle and update graph
        for j in range(3) :          # blow out and data which might be left over from 
            for ch in range(2) :     # a previous triggering.  At reasonable frequencies
                scope.getSamples(ch) # this is transparent.
        x = scope.getSamples(1) # Get data we WILL use
        y = scope.getSamples(2)
        t = np.array(range(np.size(x)))*timebase*12/600
        signal_plot.clear()
        signal_plot.plot(t,x,"r.")
        signal_plot.plot(t,y,"b.")
        (x_amp, x_period, x_phase_delay, x_crossings) = characterize(x)
        (y_amp, y_period, y_phase_delay, y_crossings) = characterize(y)
        gain = (y_amp*y_gain) / (x_amp*x_gain) # convert from samples to voltage here
        phase_fraction = (x_phase_delay - y_phase_delay) / x_period
        if phase_fraction > 0.5 :
            phase_fraction = phase_fraction - 1
        if phase_fraction < -0.5 :
            phase_fraction = phase_fraction + 1
        phase =  2*np.pi * phase_fraction
        mag_plot.plot(frequency,gain,"kx")
        phase_plot.plot(frequency,phase,"kx")
        # store values for return
        gains.append(gain)
        phases.append(phase)
    gen.local()
    scope.local()
    plt.pause(2) # leave graph up for an arbitrary period
    return (np.array(gains),np.array(phases))


# Example usage
# gets data from 1kHz to 50kHz with 50 datapoints in between
(gains, phases) = bode (np.linspace(1e3,50e3,50))