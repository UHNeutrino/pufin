# Quick Reference

> *...references under construction...*

<!-- Variable Keys Dropdown -->
<details open>

<summary> <b>
  Variable Keys
</b> </summary>

<!-- Opens Inline Tables -->
<table>
<tr>
  
<!-- Left Table -->
<td valign="top">
<table>
 <tr> <h2> &nbsp; Heading 1 </h2> </tr>
 <tr> <td><b> Variable: </b></td>   <td><b> Key: </b></td> </tr>
 <tr> <td> q<sub>0</sub> </td>   <td>q0</td>         </tr>
 <tr> <td> q<sub>3</sub> </td>   <td> q3 </td>       </tr>
 <tr> <td> Q<sup>2</sup> </td>   <td> Q2 </td>       </tr>
</table>
</td>
  
<!-- Center Table -->
<td valign="top">
<table>
  <tr> <h2> &nbsp; Heading 2 </h2> </tr>
  <tr> <td><b> Variable: </b></td>   <td><b> Key: </b></td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td>Lorem ipsum ...</td> </tr>
  <tr> <td>Lorem ipsum ...</td>   <td>Lorem ipsum ...</td> </tr>
</table>
</td>

<!-- Right Table -->
<td valign="top">
<table>
  <tr> <h2> &nbsp; Flags & Modes </h2> </tr>
  <p> note: <small> NC = Neutral Current, CC = Charged Current </small></p>
  
  <tr><td><b>Variable:</b></td>   <td><b>Key:</b></td> </tr>
  <tr> <td> Flag all CC interactions </td>   <td> flagCCINC </td> </tr>
  <tr> <td> '' all NC '' </td>   <td> flagNCINC </td> </tr>
  <tr> <td> '' CC Quasi Elastic '' </td>   <td> flagCCQE </td> </tr>
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
  <tr> <td> Interaction Modes (see below) </td>   <td> Mode</td> </tr>
</table>
</td>

<!-- Closes Inline Table -->
</tr>
</table>

</details>

<!-- Extended Variables Dropdown -->
<details>
<summary> <b>
  Extended Variable Descriptions
</b> </summary>

>This is empty right now :)
  
</details>


<!-- Frequent Modes Dropdown -->
<details>

<summary> <b>
  Frequently Used Modes
</b> </summary>

+ RES *(neutrino mode CC1pi resonant events)*:  
  ```
  Mode == 11 && Mode == 12 && Mode == 13
  ```
</details>

# NEUTRINO MODES

## CHARGED CURRENT

### ELASTIC
```
     1 : NEU,N --> LEPTON-,P
     2 : NEU,N+X --> LEPTON-,P+X  (X=(N or P))
```

### SINGLE PI FROM DELTA RESONANCE
```
    11 : NEU,P --> LEPTON-,P,PI+
    12 : NEU,N --> LEPTON-,P,PI0
    13 : NEU,N --> LEPTON-,N,PI+

    15 : NEU,P --> LEPTON-,P,PI+  ( diffractive )
    16 : NEU,O(16) --> LEPTON-,O(16),PI+
```

### SINGLE GAMMA FROM DELTA RESONANCE
```
    17 : NEU,N --> LEPTON-,P,GAMMA
```

### SINGLE K : STRANGENESS VIOLATED MODE
```
    18 : NEU,N --> LEPTON-,N,K+
    19 : NEU,N --> LEPTON-,P,K0
    20 : NEU,N --> LEPTON-,P,K+
```

### MULTI PI (1.3 < W < 2.0 GeV)
```
    21 : NEU,(N OR P) --> LEPTON-,(N OR P),MULTI PI
```

### SINGLE ETA FROM DELTA RESONANCE
```
    22 : NEU,N --> LEPTON-,P,ETA0
```

### SINGLE K FROM DELTA RESONANCE
```
    23 : NEU,N --> LEPTON-,LAMBDA,K+
```

### DEEP INELASTIC (2.0 GeV < W, JET set)
```
    26 : NEU,(N OR P) --> LEPTON-,(N OR P),MESONS
```

## NEUTRAL CURRENT

### SINGLE PI FROM DELTA RESONANCE
```
    31 : NEU,N --> NEU,N,PI0
    32 : NEU,P --> NEU,P,PI0
    33 : NEU,N --> NEU,P,PI-
    34 : NEU,P --> NEU,N,PI+

    35 : NEU,P --> NEU,P,PI0 ( diffractive )
    36 : NEU,O(16) --> NEU,O(16),PI0
```

### SINGLE GAMMA FROM DELTA RESONANCE
```
    38 : NEU,N --> NEU,N,GAMMA
    39 : NEU,P --> NEU,P,GAMMA
```

### MULTI PI (1.3 GeV < W < 2.0 GeV)
```
    41 : NEU,(N OR P) --> NEU,(N OR P),MULTI PI
```

### SINGLE ETA FROM DELTA RESONANCE
```
    42 : NEU,N --> NEU,N,ETA0
    43 : NEU,P --> NEU,P,ETA0
```

### SINGLE K FROM DELTA RESONANCE
```
    44 : NEU,N --> NEU,LAMBDA,K0
    45 : NEU,P --> NEU,LAMBDA,K+
```

### DEEP INELASTIC (2.0 GeV < W, JET set)
```
    46 : NEU,(N OR P) --> NEU,(N OR P),MESONS
```

### ELASTIC
```
    51 : NEU,P --> NEU,P
    52 : NEU,N --> NEU,N
```

# ANTI NEUTRINO MODES

## CHARGED CURRENT

### ELASTIC
```
    -1 : NEUBAR,P --> LEPTON+,N
    -2 : NEU,P+X  --> LEPTON-,N+X  (X=(N or P))
```

### SINGLE PI FROM DELTA RESONANCE
```
   -11 : NEUBAR,N --> LEPTON+,N,PI-
   -12 : NEUBAR,P --> LEPTON+,N,PI0
   -13 : NEUBAR,P --> LEPTON+,P,PI-

   -15 : NEUBAR,P --> LEPTON+,P,PI-  ( diffractive )
   -16 : NEUBAR,O(16) --> LEPTON+,O(16),PI-
```

### SINGLE GAMMA FROM DELTA RESONANCE
```
   -17 : NEUBAR,P --> LEPTON+,N,GAMMA
```

### MULTI PI (W > 1.4 GeV)
```
   -21 : NEUBAR,(N OR P) --> LEPTON+,(N OR P),MULTI PI
```

### SINGLE ETA FROM DELTA RESONANCE
```
   -22 : NEUBAR,P --> LEPTON+,N,ETA0
```

### SINGLE K FROM DELTA RESONANCE
```
   -23 : NEUBAR,P --> LEPTON+,LAMBDA,K0
```

### DEEP INELASTIC (2.0 GeV < W, JET set)
```
   -26 : NEUBAR,(N OR P) --> LEPTON+,(N OR P),MESONS
```

## NEUTRAL CURRENT

### SINGLE PI FROM DELTA RESONANCE
```
   -31 : NEUBAR,N --> NEUBAR,N,PI0
   -32 : NEUBAR,P --> NEUBAR,P,PI0
   -33 : NEUBAR,N --> NEUBAR,P,PI-
   -34 : NEUBAR,P --> NEUBAR,N,PI+

   -35 : NEUBAR,P --> LEPTON+,P,PI0  ( diffractive )
   -36 : NEUBAR,O(16) --> NEUBAR,O(16),PI0
```

### SINGLE GAMMA FROM DELTA RESONANCE
```
   -38 : NEUBAR,N --> NEUBAR,N,GAMMA
   -39 : NEUBAR,P --> NEUBAR,P,GAMMA
```

### MULTI PI (W > 1.4 GeV)
```
   -41 : NEUBAR,(N OR P) --> NEUBAR,(N OR P),MULTI PI
```

### SINGLE ETA FROM DELTA RESONANCE
```
   -42 : NEUBAR,N --> NEUBAR,N,ETA0
   -43 : NEUBAR,P --> NEUBAR,P,ETA0
```

### SINGLE K FROM DELTA RESONANCE
```
   -44 : NEUBAR,N --> NEUBAR,LAMBDA,K0
   -45 : NEUBAR,P --> NEUBAR,LAMBDA,K+
```

### DEEP INELASTIC (2.0 GeV < W, JET set)
```
   -46 : NEUBAR,(N OR P) --> NEUBAR,(N OR P),MESONS
```

### ELASTIC
```
   -51 : NEUBAR,P --> NEUBAR,P
   -52 : NEUBAR,N --> NEUBAR,N
```
