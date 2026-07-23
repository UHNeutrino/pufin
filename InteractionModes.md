# Quick Reference


<table>
<tr>
<td valign="top">
<!-- Opens Inline Tables -->

<!-- Left Table -->
<table>
  <tr>
    <b> &nbsp; Momentum </b>
  </tr>
 <tr>
    <td><b>Variable</b></td>
    <td><b>Key</b></td>
 </tr>
 <tr>
    <td> q<sub>0</sub> </td>
    <td>q0</td>
 </tr>
 <tr>
    <td> q<sub>3</sub> </td>
    <td> q3 </td>
 </tr>
 <tr>
    <td> Q<sup>2</sup> </td>
    <td> Q2 </td>
 </tr>
</table>

</td>
<td valign="top">

<!-- Center Table -->
<table>
  <tr>
    <b> &nbsp; Heading 2 </b>
  </tr>
 <tr>
    <td><b>Variable</b></td>
    <td><b>Key</b></td>
 </tr>
 <tr>
    <td>Lorem ipsum ...</td>
    <td>Lorem ipsum ...</td>
 </tr>
 <tr>
    <td>Lorem ipsum ...</td>
    <td>Lorem ipsum ...</td>
 </tr>
 <tr>
    <td>Lorem ipsum ...</td>
    <td>Lorem ipsum ...</td>
 </tr>
</table>

</td>
<td valign="top">

<!-- Right Table -->
<table>
  <tr>
    <b> &nbsp; Heading 3 </b>
  </tr>
 <tr>
    <td><b>Variable</b></td>
    <td><b>Key</b></td>
 </tr>
 <tr>
    <td>Lorem ipsum ...</td>
    <td>Lorem ipsum ...</td>
 </tr>
 <tr>
    <td>Lorem ipsum ...</td>
    <td>Lorem ipsum ...</td>
 </tr>
 <tr>
    <td>Lorem ipsum ...</td>
    <td>Lorem ipsum ...</td>
 </tr>
</table>

<!-- Close Inline Table -->
</td>
</tr>
</table>



+ RES *(neutrino mode CC1pi resonant events)*:  
  ```
  Mode == 11 && Mode == 12 && Mode == 13
  ```

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
