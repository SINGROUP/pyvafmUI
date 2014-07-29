'Block #0'
import sys
sys.path.append('/home/keisano1/Project/pyvafm-master/src')

from vafmbase import ChannelType
from vafmcircuits import Machine
from customs_pll import *
import vafmcircuits

machine = Machine(name='machine', dt = 5e-8, pushed=True)


'Block #1'
canti = machine.AddCircuit(type='Cantilever', name='canti', startingz = 0.5, Q = 10000, k=167, f0 = 150000, pushed = True)
machine.AddCircuit(type='Machine', name = 'amp', assembly = aAMPD, fcut=10000, pushed = True)
machine.AddCircuit(type='PI', name='agc',set = 1, Kp = 1.1, Ki = 800, pushed = True)
machine.AddCircuit(type='limiter', name='agclim', min = 0, max = 10, pushed = True)
machine.AddCircuit(type='Machine', name = 'pll', assembly = aPLL, filters=[10000, 5000, 2000], gain = 600, f0 = 150000, Kp = 0.5, Ki = 700, pushed = True)
machine.AddCircuit(type='opMul', name='pllinv', in2 = -1, pushed = True)
machine.AddCircuit(type='opMul', name='exc', pushed = True)
scan = machine.AddCircuit(type='Scanner', name='scan', pushed = True)


inter = machine.AddCircuit(type = 'i3Dlin', name = 'inter', components = 3, pushed = True)
inter.Configure(steps = [0.705, 0.705, 0.1], npoints = [8, 8, 201], pbc = [True, True, False])
inter.ReadData('/home/keisano1/Project/UIPyVAFM/scripts/NaClforces.dat')

image = machine.AddCircuit(type='output', name='image', file = 'tut5.dat', dump = 0, pushed = True)



'Block #2'
machine.Connect("scan.x", "inter.x")
machine.Connect("scan.y", "inter.y")
machine.Connect("scan.z", "canti.holderz")
machine.Connect("canti.zabs", "inter.z")
machine.Connect("inter.F3", "canti.fz")
machine.Connect("canti.ztip", "amp.signal")
machine.Connect("amp.amp", "agc.signal")
machine.Connect("amp.norm", "pll.signal1")
machine.Connect("pll.cos", "pll.signal2")
machine.Connect("agc.out", "agclim.signal")
machine.Connect("agclim.out", "exc.in1")
machine.Connect("pll.cos", "pllinv.in1")
machine.Connect("pllinv.out", "exc.in2")
machine.Connect("exc.out", "canti.exciter")
machine.Connect("scan.record", "image.record")


'Block #3'
scan.Recorder = image
scan.BlankLines = True
scan.Resolution = [20, 20]
scan.ImageArea(11.28, 11.28)
image.Register('scan.x', 'scan.y', 'pll.df')




'Block #4'
scan.Place(x=0, y=0, z=15)
machine.Wait(0.5)
scan.Move(x=0, y=0, z=-11)
machine.Wait(1)
scan.ScanArea()


