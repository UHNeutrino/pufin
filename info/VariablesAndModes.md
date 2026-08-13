> Not what you're looking for? Click [here](../README.md) to return to the main PUfIN README
 
# Variables & Modes
PUfIN is compatible with standard and custom variable keys as well as Nuisance [Interaction Modes](#interaction-modes), which are detailed in the following document.
 
<details>
<summary><h2> Outline </h2></summary>
  
+ [Variables & Usage](#variables--usage)
  + Standard Variable Keys
    + [Energy, Transfer, & Momentum](#energy-transfer-momentum)
    + [Invariant Mass, Position, & Miscellaneous](#invariant-mass-position--misc)
    + [Flags & Modes](#flags--modes)
  + PUfIN Custom Variable Keys
    + [Evis Variables](#evis-variables)
    + [Kinematic Variables](#kinematic-variables)
    + [TKI Variables](#tki-variables)
    + [Threshold Flags](#threshold-flags)
  + Table of Abbreviations
  + Extended Variable Descriptions
  + [Making Cuts with Variables, Flags, & Modes](#making-cuts-with-variables-flags--modes)
  + [Using PUfIN Custom Variables](#using-pufin-custom-variables)
    + Custom Variable Activation Settings
+ [Interaction Modes](#interaction-modes)
  + Frequently Used Modes 
  + [Neutrino Modes](#neutrino-modes)
    + [Charged Current](#charged-current)
    + [Neutral Current](#neutral-current)
  + [Anti Neutrino Modes](#anti-neutrino-modes)
    + [Charged Current](#charged-current-1)
    + [Neutral Current](#neutral-current-1)
   
</details>

# Variables & Usage
 
> *...under construction...*
 
<!-- Variable Keys Dropdown -->
<details open>
<summary> <b>
  Standard Variable Keys
</b> </summary>
<!-- Opens Inline Tables -->
<table>
<tr>
  
<!-- Left Table -->
<td valign="top">
<table>
 <tr> <h2 id="energy-transfer-momentum"> Energy, Transfer, & Momentum </h2> </tr>
 <tr> <td><b> Variable: </b></td>   <td><b> Key: </b></td> </tr>

  <tr> <td>Lorem ipsum ...</td>   <td> E </td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td> E_init </td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td> E_vert </td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td> E_pdg </td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td> EavAlt </td> </tr>
  
  <tr> <td> True E<sub>&nu;</sub> (neutrino energy) </td>   <td> Enu_true </td> </tr>
  <tr> <td> (Reco) E<sub>&nu;</sub><sup>QE</sup> </td>   <td> Enu_QE </td> </tr>
  <tr> <td> Lepton energy (post-FSI?) </td>   <td> ELep </td> </tr>
  <tr> <td> E<sub>miss</sub> (missing energy) </td>   <td> Emiss </td> </tr>
  <tr> <td> E<sub>miss</sub> pre-FSI </td>   <td> Emiss_preFSI </td> </tr>
  <tr> <td> Lorem ipsum ...</td>   <td> Erecoil_minerva </td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td> Erecoil_charged </td> </tr>
  

  
  
  <tr> <td>Lorem ipsum ...</td>   <td>Lorem ipsum ...</td> </tr>
  <tr> <td> q<sub>0</sub> (energy transfer) </td>   <td>q0</td>     </tr>
  <tr> <td> q<sub>3</sub> (3-momentum transfer) </td>   <td> q3 </td>  </tr>
  <tr> <td> Q<sup>2</sup> (collision hardness/4-momentum transfer) </td>   <td> Q2 </td>  </tr>
  <tr> <td> (Reco) Q<sup>2, QE</sup> </td>   <td> Q2_QE </td> </tr>
  
  <tr> <td>Lorem ipsum ...</td>   <td> px </td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td> py </td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td> pz </td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td> px_init </td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td> py_init </td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td> pz_init </td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td> px_vert </td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td> py_vert </td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td> pz_vert </td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td> ninitp</td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td> nvertp </td> </tr>
  <!-- # <tr> <td>Lorem ipsum ...</td>   <td>Lorem ipsum ...</td> </tr> # -->
</table>
</td>
  
<!-- Table 2 -->
<td valign="top">
<table>
 <tr> <h2 id="invariant-mass-position--misc"> Invariant Mass, Position, & Misc. </h2> </tr>
 <tr> <td><b> Variable: </b></td>   <td><b> Key: </b></td> </tr>
 <tr> <td> W (invariant mass) </td>   <td> W </td> </tr>
 <tr> <td> W as predicted by GENIE (?) </td>   <td> W_genie </td> </tr>
 <tr> <td>Lorem ipsum ...</td>   <td> W_nuc_rest </td> </tr>
 
 <tr> <td> Lorem ipsum ... </td>   <td> x </td> </tr>
 <tr> <td> Lorem ipsum ...</td>   <td> y </td> </tr>

 <tr> <td>Lorem ipsum ...</td>   <td> CosLep </td> </tr>
 <tr> <td>Lorem ipsum ...</td>   <td> CosThetaAdler </td> </tr>
 <tr> <td>Lorem ipsum ...</td>   <td> PhiAdler </td> </tr>
 
 <tr> <td> &delta;&alpha;<sub>T</sub> </td>   <td> dalphat </td> </tr>
 <tr> <td> &delta; p<sub>T</sub> </td>   <td> dpt </td> </tr>
 <tr> <td>Lorem ipsum ...</td>   <td> dphit </td> </tr>
 
 <tr> <td>Lorem ipsum ...</td>   <td> tgt </td> </tr>
 <tr> <td>Lorem ipsum ...</td>   <td> tgta </td> </tr>
 <tr> <td>Lorem ipsum ...</td>   <td> tgtz </td> </tr>
 
 <tr> <td>Lorem ipsum ...</td>   <td> cc </td> </tr>
 <tr> <td>Lorem ipsum ...</td>   <td> pdg </td> </tr>
 <tr> <td>Lorem ipsum ...</td>   <td> pdg_rank </td> </tr>
 <tr> <td>Lorem ipsum ...</td>   <td> pnreco_C </td> </tr>
 <tr> <td>Lorem ipsum ...</td>   <td> nfsp </td> </tr>
 <tr> <td>Lorem ipsum ...</td>   <td> PDGnu </td> </tr>
  
 <tr> <td>Lorem ipsum ...</td>   <td> Weight </td> </tr>
 <tr> <td>Lorem ipsum ...</td>   <td> InputWeight </td> </tr>
 <tr> <td>Lorem ipsum ...</td>   <td> RWWeight </td> </tr>
 <tr> <td>Lorem ipsum ...</td>   <td> fScaleFactor </td> </tr>
 <tr> <td>Lorem ipsum ...</td>   <td> CustomWeight </td> </tr>
 <tr> <td>Lorem ipsum ...</td>   <td> CustomWeightArray </td> </tr>
</table>
</td>
<!-- Table 3 -->
<td valign="top">
<table>
  <tr> <h2 id="flags--modes"> Flags & Modes </h2> </tr>
  <tr><td><b> Flag(s): </b></td>   <td><b>Key:</b></td> </tr>
  
  <tr> <td> all CC </td>   <td> flagCCINC </td> </tr>
  <tr> <td> all NC </td>   <td> flagNCINC </td> </tr>
  <tr> <td> CC Quasi Elastic </td>   <td> flagCCQE </td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td> flagCC0pi </td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td> flagCCQELike </td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td> flagNCEL </td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td> flagNC0pi </td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td> flagCCcoh </td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td> flagNCcoh </td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td> flagCC1pip </td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td> flagNC1pip </td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td> flagCC1pim </td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td> flagNC1pim </td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td> flagCC1pi0 </td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td> flagNC1pi0 </td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td> flagCC0piMINERvA</td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td> flagCC0Pi_T2K_AnaI</td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td> flagCC0Pi_T2K_AnaII </td> </tr>
  <tr> <td> Interaction Modes 
    <a href="#interaction-modes">(see below)</a> 
  </td>   <td> Mode</td> </tr>
  <td>Lorem ipsum ...</td>   <td> GENIEResCode </td>
</table>
</td>
<!-- Closes Inline Table -->
</tr>
</table>
</details>
 
  <!-- PUfIN variables dropdown -->
<details open>
<summary> <b>
  PUfIN Custom Variable Keys
</b> </summary>
<!-- Opens Inline Tables -->
<table>
<tr>
<!-- Table 1 -->
<td valign="top"> 
<table>
  <tr> <h2 id="evis-variables"> Evis Variables </h2> </tr>
  <tr> <td><b> Variable: </b></td>   <td><b> Key: </b></td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td>Lorem ipsum ...</td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td>Lorem ipsum ...</td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td>Lorem ipsum ...</td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td>Lorem ipsum ...</td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td>Lorem ipsum ...</td> </tr>
</table>
</td> 
<!-- Table 2 -->
<td valign="top"> 
<table>
  <tr> <h2 id="kinematic-variables"> Kinematic Variables </h2> </tr>
  <tr> <td><b> Variable: </b></td>   <td><b> Key: </b></td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td>Lorem ipsum ...</td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td>Lorem ipsum ...</td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td>Lorem ipsum ...</td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td>Lorem ipsum ...</td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td>Lorem ipsum ...</td> </tr>
</table>
</td> 
<!-- Table 3 -->
<td valign="top"> 
<table>
  <tr> <h2 id="tki-variables"> TKI Variables </h2> </tr>
  <tr> <td><b> Variable: </b></td>   <td><b> Key: </b></td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td>Lorem ipsum ...</td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td>Lorem ipsum ...</td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td>Lorem ipsum ...</td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td>Lorem ipsum ...</td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td>Lorem ipsum ...</td> </tr>
</table>
</td> 
<!-- Table 4 -->
<td valign="top"> 
<table>
  <tr> <h2 id="threshold-flags"> Threshold Flags </h2> </tr>
  <tr> <td><b> Variable: </b></td>   <td><b> Key: </b></td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td>Lorem ipsum ...</td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td>Lorem ipsum ...</td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td>Lorem ipsum ...</td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td>Lorem ipsum ...</td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td>Lorem ipsum ...</td> </tr>
</table>
</td> 
<!-- Closes Inline Table -->
</tr>
</table>
<!-- add variables from EvisB, KinematicsB, 
TKI (transverse kinematic imbalance), etc. from src/ParticlePlots 
> Evis_2 = calorimetric reconstruction -->
</details>
 
<!-- Abbreviations Dropdown -->
<details>
<summary> <b>
  Table of Abbreviations
</b> </summary>
<table>
  <!-- <tr> <h2> Header </h2> </tr> -->
  <tr> <td><b> Abbreviation: </b></td>   <td><b> Meaning: </b></td> </tr>
  
  <tr> <td> NC </td>   <td> Neutral Current </td> </tr>
  <tr> <td> CC </td>   <td> Charged Current</td> </tr>
  <tr> <td> QE </td>   <td> Quasi-elastic </td> </tr>
  <tr> <td> EL </td>   <td> Elastic </td> </tr>
  <tr> <td> FSI </td>   <td> Final State Interaction(s) </td> </tr>
  <tr> <td> TKI </td>   <td> Transverse Kinematic Imbalance </td> </tr>
  <tr> <td> Reco </td>   <td> Reconstruction/Reconstructed </td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td>Lorem ipsum ...</td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td>Lorem ipsum ...</td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td>Lorem ipsum ...</td> </tr>
  <!-- will alphabetize or categorize when I'm "done" -->
</table>
  
</details>
 
<!-- Extended Variables Dropdown -->
<details>
<summary> <b>
  Extended Variable Descriptions
</b> </summary>
  
<!-- reco E_nu QE equation -->
$$
E_\nu^{QE, rec} = \frac{m_p^2 - m_\ell^2 - (m_n - E_\text{b})^2 + 2E_\ell(m_n - E_\text{b})} {2(m_n - E_\text{b} - E_\ell + p_\ell^z)} 
$$
  
</details>

## Making Cuts with Variables, [Flags, & Modes](#flags--modes)
>This is empty right now :)
<!-- Explain using modes, flags, and operators to select events or interaction types -->
 
## Using PUfIN Custom Variables
 
PUfIN comes with built-in custom variables, which are defined and computed in 
[ParticlePlots.py](../src/ParticlePlots.py). 
However, due to the added compute time used to calculate these variables, activation of these variables is required before using them. 
The custom variables and flags are separated into 4 categories--
[Evis Variables](#evis-variables), 
[Kinematic Variables](#kinematic-variables), 
[TKI Variables](#tki-variables), 
[Threshold Flags](#threshold-flags)
--and can be activated individually by setting their respective config setting to true 
(variable sets not in use should be ```false``` to minimize compute time). 
These settings are activated within ```"global":``` in your config file as follows:
 
| Activation Setting | Variable Set |
| --------------------------------| -------------|
| ```"EvisB": true```             | Evis Variables|
| ```"KinematicsB": true```             | Kinematic Variables|
| ```"TkiB": true```             | TKI Variables|
| ```"ThresholdsB": true```             | Threshold Flags|


# Interaction Modes

<!-- Frequent Modes Dropdown -->
<details>

<summary> <b>
  Frequently Used Modes
</b> </summary>

+ RES *(neutrino mode CC1pi resonant events)*:  
  ```
  Mode == 11 || Mode == 12 || Mode == 13
  ```
</details>


## NEUTRINO MODES
---
### Charged Current

<!-- ########## -->
<details>
<summary> <b>
ELASTIC
</b> </summary>

```
     1 : NEU,N --> LEPTON-,P
     2 : NEU,N+X --> LEPTON-,P+X  (X=(N or P))
```
</details>

<!-- ########## -->
<details>
<summary> <b>
SINGLE PI FROM DELTA RESONANCE
</b> </summary>
  
```
    11 : NEU,P --> LEPTON-,P,PI+
    12 : NEU,N --> LEPTON-,P,PI0
    13 : NEU,N --> LEPTON-,N,PI+

    15 : NEU,P --> LEPTON-,P,PI+  ( diffractive )
    16 : NEU,O(16) --> LEPTON-,O(16),PI+
```
</details>

<!-- ########## -->
<details>
<summary> <b>
SINGLE GAMMA FROM DELTA RESONANCE
</b> </summary>

```
    17 : NEU,N --> LEPTON-,P,GAMMA
```
</details>


<!-- ########## -->
<details>
<summary> <b>
SINGLE K : STRANGENESS VIOLATED MODE
</b> </summary>

```
    18 : NEU,N --> LEPTON-,N,K+
    19 : NEU,N --> LEPTON-,P,K0
    20 : NEU,N --> LEPTON-,P,K+
```
</details>


<!-- ########## -->
<details>
<summary> <b>
MULTI PI (1.3 < W < 2.0 GeV)
</b> </summary>

```
    21 : NEU,(N OR P) --> LEPTON-,(N OR P),MULTI PI
```
</details>


<!-- ########## -->
<details>
<summary> <b>
SINGLE ETA FROM DELTA RESONANCE
</b> </summary>

```
    22 : NEU,N --> LEPTON-,P,ETA0
```
</details>


<!-- ########## -->
<details>
<summary> <b>
SINGLE K FROM DELTA RESONANCE
</b> </summary>

```
    23 : NEU,N --> LEPTON-,LAMBDA,K+
```
</details>

<!-- ########## -->
<details>
<summary> <b>
DEEP INELASTIC (2.0 GeV < W, JET set)
</b> </summary>

```
    26 : NEU,(N OR P) --> LEPTON-,(N OR P),MESONS
```
</details>

---
### Neutral Current

<!-- ########## -->
<details>
<summary> <b>
SINGLE PI FROM DELTA RESONANCE
</b> </summary>

```
    31 : NEU,N --> NEU,N,PI0
    32 : NEU,P --> NEU,P,PI0
    33 : NEU,N --> NEU,P,PI-
    34 : NEU,P --> NEU,N,PI+

    35 : NEU,P --> NEU,P,PI0 ( diffractive )
    36 : NEU,O(16) --> NEU,O(16),PI0
```
</details>


<!-- ########## -->
<details>
<summary> <b>
SINGLE GAMMA FROM DELTA RESONANCE
</b> </summary>

```
    38 : NEU,N --> NEU,N,GAMMA
    39 : NEU,P --> NEU,P,GAMMA
```
</details>


<!-- ########## -->
<details>
<summary> <b>
MULTI PI (1.3 GeV < W < 2.0 GeV)
</b> </summary>

```
    41 : NEU,(N OR P) --> NEU,(N OR P),MULTI PI
```
</details>


<!-- ########## -->
<details>
<summary> <b>
SINGLE ETA FROM DELTA RESONANCE
</b> </summary>

```
    42 : NEU,N --> NEU,N,ETA0
    43 : NEU,P --> NEU,P,ETA0
```
</details>



<!-- ########## -->
<details>
<summary> <b>
SINGLE K FROM DELTA RESONANCE
</b> </summary>

```
    44 : NEU,N --> NEU,LAMBDA,K0
    45 : NEU,P --> NEU,LAMBDA,K+
```
</details>


<!-- ########## -->
<details>
<summary> <b>
DEEP INELASTIC (2.0 GeV < W, JET set)
</b> </summary>

```
    46 : NEU,(N OR P) --> NEU,(N OR P),MESONS
```
</details>



<!-- ########## -->
<details>
<summary> <b>
ELASTIC
</b> </summary>

```
    51 : NEU,P --> NEU,P
    52 : NEU,N --> NEU,N
```
</details>


## ANTI NEUTRINO MODES
---
### Charged Current

<!-- ########## -->
<details>
<summary> <b>
ELASTIC
</b> </summary>

```
    -1 : NEUBAR,P --> LEPTON+,N
    -2 : NEU,P+X  --> LEPTON-,N+X  (X=(N or P))
```
</details>


<!-- ########## -->
<details>
<summary> <b>
SINGLE PI FROM DELTA RESONANCE
</b> </summary>

```
   -11 : NEUBAR,N --> LEPTON+,N,PI-
   -12 : NEUBAR,P --> LEPTON+,N,PI0
   -13 : NEUBAR,P --> LEPTON+,P,PI-

   -15 : NEUBAR,P --> LEPTON+,P,PI-  ( diffractive )
   -16 : NEUBAR,O(16) --> LEPTON+,O(16),PI-
```
</details>
 


<!-- ########## -->
<details>
<summary> <b>
SINGLE GAMMA FROM DELTA RESONANCE
</b> </summary>

```
   -17 : NEUBAR,P --> LEPTON+,N,GAMMA
```
</details>



<!-- ########## -->
<details>
<summary> <b>
MULTI PI (W > 1.4 GeV)
</b> </summary>

```
   -21 : NEUBAR,(N OR P) --> LEPTON+,(N OR P),MULTI PI
```
</details>


<!-- ########## -->
<details>
<summary> <b>
SINGLE ETA FROM DELTA RESONANCE
</b> </summary>

```
   -22 : NEUBAR,P --> LEPTON+,N,ETA0
```
</details>



<!-- ########## -->
<details>
<summary> <b>
SINGLE K FROM DELTA RESONANCE
</b> </summary>

```
   -23 : NEUBAR,P --> LEPTON+,LAMBDA,K0
```
</details>


<!-- ########## -->
<details>
<summary> <b>
DEEP INELASTIC (2.0 GeV < W, JET set)
</b> </summary>

```
   -26 : NEUBAR,(N OR P) --> LEPTON+,(N OR P),MESONS
```
</details>

---
### Neutral Current

<!-- ########## -->
<details>
<summary> <b>
SINGLE PI FROM DELTA RESONANCE
</b> </summary>

```
   -31 : NEUBAR,N --> NEUBAR,N,PI0
   -32 : NEUBAR,P --> NEUBAR,P,PI0
   -33 : NEUBAR,N --> NEUBAR,P,PI-
   -34 : NEUBAR,P --> NEUBAR,N,PI+

   -35 : NEUBAR,P --> LEPTON+,P,PI0  ( diffractive )
   -36 : NEUBAR,O(16) --> NEUBAR,O(16),PI0
```
</details>



<!-- ########## -->
<details>
<summary> <b>
SINGLE GAMMA FROM DELTA RESONANCE
</b> </summary>

```
   -38 : NEUBAR,N --> NEUBAR,N,GAMMA
   -39 : NEUBAR,P --> NEUBAR,P,GAMMA
```
</details>



<!-- ########## -->
<details>
<summary> <b>
 MULTI PI (W > 1.4 GeV)
</b> </summary>

```
   -41 : NEUBAR,(N OR P) --> NEUBAR,(N OR P),MULTI PI
```
</details>



<!-- ########## -->
<details>
<summary> <b>
SINGLE ETA FROM DELTA RESONANCE
</b> </summary>

```
   -42 : NEUBAR,N --> NEUBAR,N,ETA0
   -43 : NEUBAR,P --> NEUBAR,P,ETA0
```
</details>



<!-- ########## -->
<details>
<summary> <b>
SINGLE K FROM DELTA RESONANCE
</b> </summary>

```
   -44 : NEUBAR,N --> NEUBAR,LAMBDA,K0
   -45 : NEUBAR,P --> NEUBAR,LAMBDA,K+
```
</details>



<!-- ########## -->
<details>
<summary> <b>
DEEP INELASTIC (2.0 GeV < W, JET set)
</b> </summary>

```
   -46 : NEUBAR,(N OR P) --> NEUBAR,(N OR P),MESONS
```
</details>



<!-- ########## -->
<details>
<summary> <b>
ELASTIC
</b> </summary>

```
   -51 : NEUBAR,P --> NEUBAR,P
   -52 : NEUBAR,N --> NEUBAR,N
```
</details>
