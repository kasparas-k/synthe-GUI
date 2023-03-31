#!/bin/bash

rm -f for*
ap=04

EXE=${EXE}
LIN=${LIN}
MOL=${MOL}

wmin=600
wmax=605
nrot=1
rot1=${VROT}
rot2=2.8
rot3=6.0

glog=1.60
temp=4600
logmet=-2.5
v=0.00


check=`echo "${logmet}*100" | bc -l`
icheck="`echo ${check} | sed  -e 's/\.//' `"
if [ ${icheck} -lt 0 ]; then
  strmet=${logmet}
else
  strmet=p${logmet}
fi


grav="`echo ${glog} | sed  -e 's/\.//'`"

met="`echo ${strmet} | sed  -e 's/\.//' -e 's/-/m/'`"

# add header necessary for the program to run
cat synthe/topINT.txt ${MODEL} > current.MOD
model=current.MOD

teff=t${temp}

ln -s ${LIN}he1tables.dat  fort.18
ln -s ${LIN}molecules.dat  fort.2
ln -s ${LIN}continua.dat   fort.17

# AIR         664.0     665.0    800000.      {v}    0     30    .0001     0    0
# AIRorVAC  WLBEG     WLEND     RESOLU    TURBV  IFNLTE LINOUT CUTOFF        NREAD
${EXE}xnfpelsyn.exe < $model
${EXE}synbeg.exe <<EOF
AIR         ${blue}     ${red}    800000.      ${v}    0     30    .0001     0    0
AIRorVAC  WLBEG     WLEND     RESOLU    TURBV  IFNLTE LINOUT CUTOFF        NREAD
EOF

 ln -s ${LIN}gfhy0300.100 fort.11
 ${EXE}rgfalllinesnew.exe
 rm -f fort.11
 ln -s ${LIN}gfhy0400.100 fort.11
 ${EXE}rgfalllinesnew.exe
 rm -f fort.11
 ln -s ${LIN}gfhy0500.100 fort.11
 ${EXE}rgfalllinesnew.exe
 rm -f fort.11
 ln -s ${LIN}gfhy0600.100 fort.11
 ${EXE}rgfalllinesnew.exe
 rm -f fort.11

ln -s ${MOL}ohaxxx.asc fort.11
${EXE}rmolecasc.exe
rm -f fort.11
ln -s ${MOL}chmasseron.asc fort.11
${EXE}rmolecasc2.exe
rm -f fort.11
ln -s ${MOL}cnaxbrookek.asc fort.11
${EXE}rmolecasc2.exe
rm -f fort.11
ln -s ${MOL}cnbxbrookek.asc fort.11
${EXE}rmolecasc2.exe
rm -f fort.11
ln -s ${MOL}cnxx12brooke.asc fort.11
${EXE}rmolecasc2.exe
rm -f fort.11
ln -s ${MOL}nhfernando.asc fort.11
${EXE}rmolecasc.exe
rm -f fort.11

${EXE}synthe.exe
outint=t${teff}g${grav}${ap}m${met}.int

cat <<EOF >fort.25
0.0       0.        1.        0.        0.        0.        0.        0.
0.
RHOXJ     R1        R101      PH1       PC1       PSI1      PRDDOP    PRDPOW
EOF
${EXE}spectrv.exe < ${model}

#
# Rotational broadening
#
mv fort.7 ${outint}
ln -s ${outint} fort.1
${EXE}rotate.exe <<EOF
    ${nrot}   50
       ${rot1}       ${rot2}       ${rot3}
EOF

rm -f for*

pippo=1
while [ $pippo -le $nrot ]
do
outspec=${teff}g${grav}${met}a${ap}_r${pippo}.flx

mv ROT${pippo} ${outspec}
#
# Macroturbulence broadening
#
ln -s ${outspec} fort.21
ln -s ${outspec} fort.1

brspec=br_${outspec}
ln -s ${brspec} fort.22
${EXE}broaden.exe << EOF
MACRO     ${VMAC}      KM        COMMENT FIELD
EOF

rm -f fort.*

#
# Instrumental broadening
#
ln -s ${brspec} fort.21
ln -s ${brspec} fort.1

insbrspec=ins_${brspec}
ln -s ${insbrspec} fort.22
${EXE}broaden.exe << EOF
GAUSSIAN   ${RESOLUTION}   RESOLUTIONCOMMENT FIELD
EOF

# Output:
# Synthetic spectrum without broadening
#asc=test_synspec_${teff}g${grav}a${ap}${met}_w${wmin}_${wmax}_r${pippo}.dat
asc=raw.dat
# Synthetic spectrum with additional broadening (rotational, macroturbulence, instrumental) included
#asc_br=test_synspec_${teff}g${grav}_br_r${pippo}.dat
asc_br=br.dat
# Spectral line identification files (both versions are identical)
#lines=test_${teff}g${grav}a${ap}${met}_w${wmin}_${wmax}_r${pippo}_lin.dat
#line_br=test_${teff}g${grav}_br_r${pippo}_lin.dat
lines=lin.dat
lines_br=lin_br.dat


rm -f fort.2
ln -s $lines fort.3
ln -s $asc   fort.2
ln -s dmp.dmp fort.4
${EXE}syntoascanga.exe

rm -f fort.1
rm -f fort.2
rm -f fort.3

ln -s ${insbrspec} fort.1
ln -s $lines_br fort.3
ln -s $asc_br fort.2
${EXE}syntoascanga.exe

rm -f for*

date

pippo=$(( $pippo + 1 ))
done
