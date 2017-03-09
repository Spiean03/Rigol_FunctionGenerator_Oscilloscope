# Rigol_FunctionGenerator_Oscilloscope
Rigol DG1022U Function Generator and Rigol DS1102E Oscilloscope Python Interface


Example Function Generator:
---------------------------

```python
import instruments.py

gen = Generator() # Connects to the Function Generator
gen.sine(1,1000,2) # Produces a sine wave on CH1, with frequency 1000Hz and Amplitude 2V
```
Example Oscilloscope:
---------------------
```python
scope = Scope() # Connects to the Oscilloscope
timebase = scope.setTimebase(0.001) # Set horizontal scale to 0.001 seconds per division
voltsPerDivision = scope.setVerticalGain(1,1.0) # Set CH1 to 1V per division
y = scope.getSamples(1) # Record the data from one trigger into vector y
```
