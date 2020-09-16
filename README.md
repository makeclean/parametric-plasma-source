# parametric-plasma-source

![Python package](https://github.com/DanShort12/parametric-plasma-source/workflows/Python%20package/badge.svg)

Python package, C++ source and build files for parametric plasma source for use in fusion neutron transport calculations with OpenMC.

The plasma source is based on a paper by [C. Fausser et al](https://www.sciencedirect.com/science/article/pii/S0920379612000853)

## Installation

```pip install parametric_plasma_source```

## Usage

The parametric plasma source can be imported an used in Python 3 in the following manner.

```[python]
from parametric_plasma_source import Plasma
my_plasma = Plasma(major_radius=6,
                   minor_radius=1.5,
                   elongation = 2.0
                   triangularity = 0.55)
my_plasma.export_plasma_source('custom_openmc_plasma_source.so')
```

In the above example the major_radius, minor_radius, elongation and triangularity while the other varibles are kept as the default values.

There are a number of additional arguments that can be passed to the Plasma class on construction. Units are in SI (e.g. meters not cm)

```[python]
ion_density_pedistal = 1.09e+20
ion_density_seperatrix = 3e+19
ion_density_origin = 1.09e+20
ion_temperature_pedistal = 6.09
ion_temperature_seperatrix = 0.1
ion_temperature_origin = 45.9
pedistal_radius = 0.8
ion_density_peaking_factor = 1
ion_temperature_peaking_factor = 8.06
minor_radius = 1.56
major_radius = 2.5
elongation = 2.0
triangularity = 0.55
shafranov_shift = 0.0
number_of_bins = 100
plasma_type = 1
```

For a better understanding of the varibles take a look at the [C. Fausser et al](https://www.sciencedirect.com/science/article/pii/S0920379612000853) paper.

## C API for use with Fortran

A C API is provided for linking of the plasma source routine to Fortran. This is particularly useful for compilation with MCNP. To compile a static library and a test program a build script is provided in the ```parametric-plasma-source/parametric_plasma_source/fortran_api``` folder. This can be run in the following manner:

```[bash]
cd parametric-plasma-source/parametric_plasma_source/fortran_api
./build_lib.sh intel
```
for use with intel ifort and icpc compilers or
```[bash]
cd parametric-plasma-source/parametric_plasma_source/fortran_api
./build_lib.sh gnu
```
for use with the gnu gfortran and g++ compilers.

### Use with MCNP

In order to use the library with MCNPv6.2 the ```plasma_source_module.F90``` and ```mcnp_pp.F90``` should be placed in the ```src``` folder. The ```source.F90``` provided with MCNP should then be modified to:

```[fortran]
subroutine source

  ! .. Use Statements ..
  use mcnp_interfaces_mod, only : expirx
  use mcnp_debug
  use pp_source_mk2_mod

  implicit none

  call parametric_plasma_2

  return
end subroutine source
```
The MCNP Makefile should also be updated to point to the library during linking. This can be done by adding the first line and modifying the second line in the Makefile:
```
PPLIB = -lplasmasource -L$(PLASMA_SOURCE)
COMPILE_LINE=$(LD) $(OUT_EXE)$(EXEC) $(F_OBJS) $(C_OBJS) $(ALL_LDFLAGS) $(PLOTLIBS) $(LIB_DMMP) $(EXTRALIBS) \
             $(PPLIB)
```
When compiling MCNP the PLASMA_SOURCE variable then needs to be set to the folder containing ```libplasmasource.a```. An example of the compliation line would be:

```
make build CONFIG='intel openmpi omp plot' PLASMA_SOURCE=/plasma/source/dir/
```

The source parameters are passed using the rdum and idum cards in the mcnp input file

```[fortran]
ion_density_pedistal           = rdum(1)
ion_density_seperatrix         = rdum(2)
ion_density_origin             = rdum(3)
ion_temperature_pedistal       = rdum(4)
ion_temperature_seperatrix     = rdum(5)
ion_temperature_origin         = rdum(6)
ion_density_peaking_factor     = rdum(7)
ion_temperature_peaking_factor = rdum(8)
ion_temperature_beta           = rdum(9)
minor_radius                   = rdum(10)
major_radius                   = rdum(11)
pedistal_radius                = rdum(12)
elongation                     = rdum(13)
triangularity                  = rdum(14)
min_toroidal_angle             = rdum(15)
max_toroidal_angle             = rdum(16)
        
number_of_bins                 = idum(2)
plasma_id                      = idum(3)
```
Note that idum(1) is intentionally left unused. This can be used for source selection if multiple user defined sources are to be compiled in the same executable. 
