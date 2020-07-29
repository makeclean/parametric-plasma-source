#include <iostream>
#include "openmc/random_lcg.h"
#include "openmc/source.h"
#include "openmc/particle.h"
#include "plasma_source.hpp"
#include "enums.hpp"


// Spherical tokamak SOURCE 
const double ion_density_pedistal = 1.09e+20; // ions per m^3
const double ion_density_seperatrix =3e+19;
const double ion_density_origin = 1.09e+20;
const double ion_temperature_pedistal = 6.09;
const double ion_temperature_seperatrix = 0.1;
const double ion_temperature_origin = 45.9;
const double ion_density_peaking_factor = 1;
const double ion_temperature_peaking_factor = 8.06; // check alpha or beta value from paper
const double ion_temperature_beta = 6.0;
const double minor_radius = 1.56; // metres
const double major_radius = 2.5; // metres
const double pedistal_radius = 0.8 * minor_radius; // pedistal minor rad in metres
const double elongation = 2.0;
const double triangularity = 0.55;
const double shafranov_shift = 0.0; //metres
const std::string name = "parametric_plasma_source";
const int number_of_bins  = 100;
const int plasma_type = 1; // 1 is default; //0 = L mode anything else H/A mode
const plasma_source::valid_basis basis = plasma_source::valid_basis::XYZ; // XYZ for 3D, RY or RZ for 2D



plasma_source::PlasmaSource source = plasma_source::PlasmaSource(ion_density_pedistal,
       ion_density_seperatrix,
       ion_density_origin,
       ion_temperature_pedistal,
       ion_temperature_seperatrix,
       ion_temperature_origin,
       pedistal_radius,
       ion_density_peaking_factor,
       ion_temperature_peaking_factor,
       ion_temperature_beta,
       minor_radius,
       major_radius,
       elongation,
       triangularity,
       shafranov_shift,
       name,
       plasma_type,
       number_of_bins,
       0.0,
       360.0);
  
// you must have external C linkage here otherwise 
// dlopen will not find the file
extern "C" openmc::Particle::Bank sample_source(uint64_t* seed) {
    openmc::Particle::Bank particle;
    // wgt
    particle.particle = openmc::Particle::Type::neutron;
    particle.wgt = 1.0;
    // position 

    std::array<double,8> randoms = {openmc::prn(seed),
                                    openmc::prn(seed),
                                    openmc::prn(seed),
                                    openmc::prn(seed),
                                    openmc::prn(seed),
                                    openmc::prn(seed),
                                    openmc::prn(seed),
                                    openmc::prn(seed)};

    double u,v,w,E;
    source.SampleSource(randoms,particle.r.x,particle.r.y,particle.r.z,
                        u,v,w,E); 

    // Convert m to cm
    particle.r.x *= 100.;
    particle.r.y *= 100.;
    particle.r.z *= 100.;

    if(basis == plasma_source::valid_basis::XYZ) {
        // Use values as-is
    }
    else if(basis == plasma_source::valid_basis::RY) {
        particle.r.x = std::sqrt(std::pow(particle.r.x, 2) + std::pow(particle.r.y, 2));
        particle.r.y = particle.r.z;
        particle.r.z = 0.;
    }
    else if(basis == plasma_source::valid_basis::RZ) {
        particle.r.x = std::sqrt(std::pow(particle.r.x, 2) + std::pow(particle.r.y, 2));
        particle.r.y = 0.;
        particle.r.z = particle.r.z;
    }
    else {
        throw std::runtime_error("Parametric plasma source: incorrect basis provided, "
                                 "please use XYZ, RY, or RZ.");
    }
   
    // particle.E = 14.08e6;
    particle.E = E*1e6; // convert from MeV -> eV

    particle.u = {u,
                  v,
                  w};

    
    particle.delayed_group = 0;
    return particle;    
}


