import sys
import os
import pytest

# Add src directory to path to import server
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from enigmapython_mcp.server import encrypt_message, RotorConfig, ReflectorConfig

def test_enigma_i_1930():
    """
    Verifies the decryption of the authentic 1930 German Army Enigma test message.
    Source: https://cryptocellar.org/enigma/e-message-1930.html
    Left to Right: II, I, III
    Fastest to Slowest: III, I, II
    Rings (0-based): 21, 12, 23
    Pos (0-based): 11, 1, 0
    """
    rotors = [
        RotorConfig(rotor_type="III", ring_setting=21, initial_position=11),
        RotorConfig(rotor_type="I", ring_setting=12, initial_position=1),
        RotorConfig(rotor_type="II", ring_setting=23, initial_position=0)
    ]
    reflector = ReflectorConfig(reflector_type="UKWA")
    plugboard = {"A": "M", "F": "I", "N": "V", "P": "S", "T": "U", "W": "Z"}
    
    ciphertext = "GCDSE AHUGW TQGRK VLFGX UCALX VYMIG MMNMF DXTGN VHVRM MEVOU YFZSL RHDRR XFJWC FHUHM UNZEF RDISI KBGPM YVXUZ".replace(" ", "").lower()
    expected_plaintext = "FEIND LIQEI NFANT ERIEK OLONN EBEOB AQTET XANFA NGSUE DAUSG ANGBA ERWAL DEXEN DEDRE IKMOS TWAER TSNEU STADT".replace(" ", "").lower()
    
    plaintext = encrypt_message("I", ciphertext, rotors, reflector, plugboard)
    assert plaintext == expected_plaintext

def test_m4_u534():
    """
    Verifies the decryption of the U534 M4 message P1030700.
    Source: https://enigma.hoerenberg.com/index.php?cat=The%20U534%20messages&page=P1030700
    Left to Right: Gamma, IV, III, VIII
    Fastest to Slowest: VIII, III, IV, Gamma
    Rings (0-based): 20, 2, 0, 0
    Pos (0-based): 2, 6, 12, 21
    """
    rotors = [
        RotorConfig(rotor_type="VIII", ring_setting=20, initial_position=2),
        RotorConfig(rotor_type="III", ring_setting=2, initial_position=6),
        RotorConfig(rotor_type="IV", ring_setting=0, initial_position=12),
        RotorConfig(rotor_type="Gamma", ring_setting=0, initial_position=21)
    ]
    reflector = ReflectorConfig(reflector_type="UKWBThin")
    plugboard = {"C": "H", "E": "J", "N": "V", "O": "U", "T": "Y", "L": "G", "S": "Z", "P": "K", "D": "I", "Q": "B"}
    
    ciphertext = "QBHEWTDFEQITKUWFQUHLIQQGVYGRSDOHDCOBFMDHXSKOFPAODRSVBEREIQZVEDAXSHOHBIYMCIIZSKGNDLNFKFVLWWHZXZGQXWSSPWLSOQXEANCELJYJCETZTLSTTWMTOBW".lower()
    expected_plaintext = "KOMXBDMXUUUBOOTEYFXDXUUUAUSBILVUNYYZWOSECHSXUUUFLOTTXVVVUUURWODREISECHSVIERKKREMASKKMITUUVZWODREIFUVFYEWHSYUUUZWODREIFUNFZWOYUUFZWL".lower()
    
    plaintext = encrypt_message("M4", ciphertext, rotors, reflector, plugboard)
    assert plaintext == expected_plaintext

def test_m3_real_payload():
    """
    Verifies M3 encryption against upstream EnigmaM3_tests.py.
    Rotors L-R: VI, V, IV
    Fastest to Slowest: IV, V, VI
    Positions: 25, 4, 15
    """
    rotors = [
        RotorConfig(rotor_type="IV", ring_setting=0, initial_position=25),
        RotorConfig(rotor_type="V", ring_setting=0, initial_position=4),
        RotorConfig(rotor_type="VI", ring_setting=0, initial_position=15)
    ]
    reflector = ReflectorConfig(reflector_type="UKWB")
    
    plaintext = "thisismyawesomeenigmasupercalifragilistichespiralidososupercalifragilistichespiralidoso"
    expected_ciphertext = "grdftnwtlegogzglhwbjgttnnwaigcpamesxheqjtxiecywvdxcncyifitbpgokalupxaambtxblvkmjlgejgdv"
    
    ciphertext = encrypt_message("M3", plaintext, rotors, reflector)
    assert ciphertext == expected_ciphertext

def test_enigma_z_real_payload():
    """
    Verifies Enigma Z encryption against upstream EnigmaZ_tests.py.
    """
    rotors = [
        RotorConfig(rotor_type="I", initial_position=0),
        RotorConfig(rotor_type="I", initial_position=0),
        RotorConfig(rotor_type="I", initial_position=0)
    ]
    reflector = ReflectorConfig(reflector_type="UKW_EnigmaZ")
    
    plaintext = "123456789012345678901234567890"
    expected_ciphertext = "719365648926063110712103315478"
    
    ciphertext = encrypt_message("Z", plaintext, rotors, reflector)
    assert ciphertext == expected_ciphertext

def test_enigma_k_verified_vector():
    """
    Test against a vector verified with dencode.com and cryptii.com
    Rotors L-R: III, II, I
    Fastest to Slowest: I, II, III
    """
    rotors = [
        RotorConfig(rotor_type="I", initial_position=0),
        RotorConfig(rotor_type="II", initial_position=0),
        RotorConfig(rotor_type="III", initial_position=0)
    ]
    reflector = ReflectorConfig(reflector_type="UKW_EnigmaCommercial")
    
    plaintext = "helloworld"
    expected_ciphertext = "acsyipzuuu"
    
    ciphertext = encrypt_message("K", plaintext, rotors, reflector)
    assert ciphertext == expected_ciphertext

# Keep reversibility for models that might not have a long known plaintext in tests easily accessible
def test_enigma_k_swiss_reversibility():
    plaintext = "swissmodel"
    rotors = [RotorConfig(rotor_type="I"), RotorConfig(rotor_type="II"), RotorConfig(rotor_type="III")]
    reflector = ReflectorConfig(reflector_type="UKW_EnigmaCommercial")
    cipher = encrypt_message("K_Swiss", plaintext, rotors, reflector)
    decrypted = encrypt_message("K_Swiss", cipher, rotors, reflector)
    assert decrypted == plaintext

def test_enigma_d_reversibility():
    plaintext = "anothercommercial"
    rotors = [RotorConfig(rotor_type="I"), RotorConfig(rotor_type="II"), RotorConfig(rotor_type="III")]
    reflector = ReflectorConfig(reflector_type="UKW_EnigmaCommercial")
    cipher = encrypt_message("D", plaintext, rotors, reflector)
    decrypted = encrypt_message("D", cipher, rotors, reflector)
    assert decrypted == plaintext

def test_enigma_b_a133_reversibility():
    plaintext = "svenskamaskin"
    rotors = [RotorConfig(rotor_type="I"), RotorConfig(rotor_type="II"), RotorConfig(rotor_type="III")]
    reflector = ReflectorConfig(reflector_type="UKW_EnigmaB_A133")
    cipher = encrypt_message("B_A133", plaintext, rotors, reflector)
    decrypted = encrypt_message("B_A133", cipher, rotors, reflector)
    assert decrypted == plaintext

def test_enigma_i_norway_reversibility():
    plaintext = "norenigma"
    rotors = [RotorConfig(rotor_type="I"), RotorConfig(rotor_type="II"), RotorConfig(rotor_type="III")]
    reflector = ReflectorConfig(reflector_type="UKW_EnigmaINorway")
    cipher = encrypt_message("I_Norway", plaintext, rotors, reflector)
    decrypted = encrypt_message("I_Norway", cipher, rotors, reflector)
    assert decrypted == plaintext

def test_enigma_i_sondermaschine_reversibility():
    plaintext = "sondermaschine"
    rotors = [RotorConfig(rotor_type="I"), RotorConfig(rotor_type="II"), RotorConfig(rotor_type="III")]
    reflector = ReflectorConfig(reflector_type="UKW_EnigmaISonder")
    cipher = encrypt_message("I_Sondermaschine", plaintext, rotors, reflector)
    decrypted = encrypt_message("I_Sondermaschine", cipher, rotors, reflector)
    assert decrypted == plaintext

def test_exhaustive_sanitization_variants():
    """
    Verifies that the server gracefully handles an extensive array of LLM formatting hallucinations 
    for machine models, rotors, and reflectors (casing, hyphens, spaces, prefixes, and word noise).
    """
    plaintext = "testmessage"
    
    # 1. Enigma M3 with messy rotor names
    rotors_m3 = [
        RotorConfig(rotor_type="Rotor III"), 
        RotorConfig(rotor_type="rotor-II"), 
        RotorConfig(rotor_type="I")
    ]
    ref_m3 = ReflectorConfig(reflector_type="UKW-B")
    assert encrypt_message("Enigma M3", plaintext, rotors_m3, ref_m3) == encrypt_message("M3", plaintext, rotors_m3, ref_m3)
    
    # 2. Enigma I_Norway
    rotors_norway = [
        RotorConfig(rotor_type="I"), 
        RotorConfig(rotor_type="II"), 
        RotorConfig(rotor_type="III")
    ]
    ref_norway = ReflectorConfig(reflector_type="UKW Enigma I Norway")
    
    # "Enigma I-Norway", "enigma_i_norway", "i norway" should all work and map to I_Norway
    cipher_a = encrypt_message("Enigma I-Norway", plaintext, rotors_norway, ref_norway)
    cipher_b = encrypt_message("enigma_i_norway", plaintext, rotors_norway, ref_norway)
    cipher_c = encrypt_message("i norway", plaintext, rotors_norway, ref_norway)
    assert cipher_a == cipher_b == cipher_c
    
    # 3. K_Swiss and D
    rotors_k = [RotorConfig(rotor_type="i"), RotorConfig(rotor_type="ii"), RotorConfig(rotor_type="iii")]
    ref_k = ReflectorConfig(reflector_type="UKW_EnigmaCommercial")
    
    cipher_d = encrypt_message("Enigma D", plaintext, rotors_k, ref_k)
    assert cipher_d == encrypt_message("d", plaintext, rotors_k, ref_k)
    
    cipher_kswiss = encrypt_message("K Swiss", plaintext, rotors_k, ref_k)
    assert cipher_kswiss == encrypt_message("k-swiss", plaintext, rotors_k, ref_k)
    
    # 4. M4 with thin reflectors and greek rotors
    rotors_m4 = [
        RotorConfig(rotor_type="ROTOR I"), 
        RotorConfig(rotor_type="rotor ii"), 
        RotorConfig(rotor_type="III"),
        RotorConfig(rotor_type="Beta")
    ]
    ref_m4_a = ReflectorConfig(reflector_type="UKW-B-Thin")
    ref_m4_b = ReflectorConfig(reflector_type="ukw b thin")
    ref_m4_c = ReflectorConfig(reflector_type="UKWBTHIN")
    ref_m4_d = ReflectorConfig(reflector_type="B-Thin Reflector")
    
    cipher_m4_a = encrypt_message("m-4", plaintext, rotors_m4, ref_m4_a)
    cipher_m4_b = encrypt_message("enigma m4", plaintext, rotors_m4, ref_m4_b)
    cipher_m4_c = encrypt_message("M4", plaintext, rotors_m4, ref_m4_c)
    cipher_m4_d = encrypt_message("M4", plaintext, rotors_m4, ref_m4_d)
    assert cipher_m4_a == cipher_m4_b == cipher_m4_c == cipher_m4_d
    
    # 5. B_A133
    rotors_b = [RotorConfig(rotor_type="I"), RotorConfig(rotor_type="II"), RotorConfig(rotor_type="III")]
    ref_b = ReflectorConfig(reflector_type="UKW Enigma B A133")
    cipher_b1 = encrypt_message("b a133", plaintext, rotors_b, ref_b)
    cipher_b2 = encrypt_message("enigma b-a133", plaintext, rotors_b, ref_b)
    assert cipher_b1 == cipher_b2
    
    # 6. Basic Reflector test
    rotors_basic = [RotorConfig(rotor_type="I"), RotorConfig(rotor_type="II"), RotorConfig(rotor_type="III")]
    ref_basic_1 = ReflectorConfig(reflector_type="A Reflector")
    ref_basic_2 = ReflectorConfig(reflector_type="ukw a")
    assert encrypt_message("I", plaintext, rotors_basic, ref_basic_1) == encrypt_message("I", plaintext, rotors_basic, ref_basic_2)
