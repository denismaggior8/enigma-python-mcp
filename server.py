import importlib
from mcp.server.fastmcp import FastMCP

# Initialize FastMCP Server
mcp = FastMCP("Enigma Server")

def get_class(module_name: str, class_name: str = None):
    """Dynamically loads a class from the enigmapython package."""
    if class_name is None:
        class_name = module_name
    module = importlib.import_module(f"enigmapython.{module_name}")
    return getattr(module, class_name)

# Configuration mapping for Enigma machine models
MODELS_CONFIG = {
    "M3": {
        "cls": "EnigmaM3",
        "etw": "EtwPassthrough",
        "has_plugboard": True,
        "default_auto_increment": True
    },
    "M4": {
        "cls": "EnigmaM4",
        "etw": "EtwPassthrough",
        "has_plugboard": True,
        "default_auto_increment": True
    },
    "I": {
        "cls": "EnigmaI",
        "etw": "EtwPassthrough",
        "has_plugboard": True,
        "default_auto_increment": True
    },
    "I_Norway": {
        "cls": "EnigmaINorway",
        "etw": "EtwPassthrough",
        "has_plugboard": True,
        "default_auto_increment": True
    },
    "I_Sondermaschine": {
        "cls": "EnigmaISonder",
        "etw": "EtwPassthrough",
        "has_plugboard": True,
        "default_auto_increment": True
    },
    "K": {
        "cls": "EnigmaK",
        "etw": "EtwQWERTZ",
        "has_plugboard": False,
        "default_auto_increment": True
    },
    "K_Swiss": {
        "cls": "EnigmaKSwiss",
        "etw": "EtwQWERTZ",
        "has_plugboard": False,
        "default_auto_increment": True
    },
    "D": {
        "cls": "EnigmaD",
        "etw": "EtwQWERTZ",
        "has_plugboard": False,
        "default_auto_increment": True
    },
    "Z": {
        "cls": "EnigmaZ",
        "etw": "EnigmaZEtw",
        "has_plugboard": False,
        "default_auto_increment": True
    },
    "B_A133": {
        "cls": "EnigmaB_A133",
        "etw": "EnigmaB_A133Etw",
        "has_plugboard": False,
        "default_auto_increment": True
    }
}

from pydantic import BaseModel, Field
from typing import List, Dict, Union

class RotorConfig(BaseModel):
    rotor_type: str = Field(description="Rotor identifier (e.g., 'I', 'II', 'Beta').")
    ring_setting: int = Field(default=0, description="Ring setting (0-25).")
    initial_position: Union[int, str] = Field(default=0, description="Initial position (0-25 or A-Z).")

class ReflectorConfig(BaseModel):
    reflector_type: str = Field(description="Reflector identifier (e.g., 'UKWA', 'UKWB', 'UKW_EnigmaCommercial').")
    ring_setting: int = Field(default=0, description="Ring setting (0-25). Only applicable for settable/rotating reflectors.")
    initial_position: Union[int, str] = Field(default=0, description="Initial position (0-25 or A-Z). Only applicable for rotating reflectors.")

@mcp.tool()
def encrypt_message(
    machine_model: str,
    message: str,
    rotors: List[RotorConfig],
    reflector: ReflectorConfig,
    plugboard_pairs: Dict[str, str] = None
) -> str:
    """
    Encrypt or decrypt a message using an Enigma machine.
    
    Args:
        machine_model: Model name. Supported models and their valid rotors/reflectors:
            - 'M3': Rotors I-VIII. Reflectors: UKWB, UKWC
            - 'M4': Rotors Beta, Gamma, I-VIII. Reflectors: UKWBThin, UKWCThin
            - 'I': Rotors I-V. Reflectors: UKWA, UKWB, UKWC
            - 'I_Norway': Rotors I-V. Reflectors: UKW_EnigmaINorway
            - 'I_Sondermaschine': Rotors I-III. Reflectors: UKW_EnigmaISonder
            - 'K': Rotors I-III. Reflectors: UKW_EnigmaCommercial
            - 'K_Swiss': Rotors I-III. Reflectors: UKW_EnigmaCommercial
            - 'D': Rotors I-III. Reflectors: UKW_EnigmaCommercial
            - 'Z': Rotors I-III. Reflectors: UKW_EnigmaZ
            - 'B_A133': Rotors I-III. Reflectors: UKW_EnigmaB_A133
        message: The plaintext or ciphertext to process.
        rotors: List of RotorConfig objects. Ordered from left to right as mechanically placed.
        reflector: The ReflectorConfig object.
        plugboard_pairs: Optional dict for plugboard connections (e.g. {"A": "B", "C": "D"}). Ignored if the machine has no plugboard.
    """
    if machine_model not in MODELS_CONFIG:
        raise ValueError(f"Unsupported machine model: {machine_model}")
        
    config = MODELS_CONFIG[machine_model]
    prefix = config["cls"] 
    
    # 1. Initialize ETW
    etw_cls = get_class(config["etw"])
    etw = etw_cls()
    
    # 2. Initialize Reflector
    reflector_cls_name = f"Reflector{reflector.reflector_type}"
    try:
        reflector_cls = get_class(reflector_cls_name)
    except ModuleNotFoundError:
        try:
            # Maybe it's a specific reflector like ReflectorUKW_EnigmaCommercial
            reflector_cls = get_class(reflector.reflector_type)
        except ModuleNotFoundError:
            raise ValueError(f"Reflector class not found: {reflector_cls_name} or {reflector.reflector_type}")
            
    import inspect
    sig = inspect.signature(reflector_cls.__init__)
    kwargs = {}
    
    if 'position' in sig.parameters:
        pos = reflector.initial_position
        if isinstance(pos, str):
            if pos.isdigit():
                pos = int(pos)
            else:
                pos = ord(pos.upper()) - 65
        kwargs['position'] = pos
        
    if 'ring' in sig.parameters:
        kwargs['ring'] = reflector.ring_setting
        
    reflector_inst = reflector_cls(**kwargs)

    # 3. Initialize Rotors
    rotor_instances = []
    for r_conf in rotors:
        r_cls_name = f"{prefix}Rotor{r_conf.rotor_type}"
        try:
            r_cls = get_class(r_cls_name)
        except ModuleNotFoundError:
            raise ValueError(f"Rotor class not found: {r_cls_name}. Check valid rotors for {machine_model}.")
        
        pos = r_conf.initial_position
        if isinstance(pos, str):
            if pos.isdigit():
                pos = int(pos)
            else:
                pos = ord(pos.upper()) - 65
                
        ring = r_conf.ring_setting
        
        # Instantiate rotor with position and ring
        rotor_instances.append(r_cls(position=pos, ring=ring))
        
    # 4. Initialize Plugboard (if applicable)
    plugboard_inst = None
    if config["has_plugboard"]:
        plugboard_cls = get_class("SwappablePlugboard")
        plugboard_inst = plugboard_cls()
        if plugboard_pairs:
            lower_pairs = {k.lower(): v.lower() for k, v in plugboard_pairs.items()}
            plugboard_inst.bulk_swap(lower_pairs)

    # 5. Build Enigma Machine
    machine_cls = get_class(config["cls"])
    
    # Different machines have different constructor signatures
    # Typically: plugboard, rotorN..rotor1, reflector, etw
    # Let's dynamically pass them based on expected parameters.
    # EnigmaM3/M4 expect rotors passed individually, reversed usually?
    # Wait, the M3 example: enigma = EnigmaM3(plugboard, rotor3, rotor2, rotor1, reflector, etw, True)
    # The M4 example: enigma = EnigmaM4(plugboard, rotor1, rotor2, rotor3, rotor4, reflector, etw, True)
    # Actually, enigmapython passes rotors from left to right mechanically. 
    # Let's inspect the constructor of the class to see how many rotors it takes.
    import inspect
    sig = inspect.signature(machine_cls.__init__)
    params = list(sig.parameters.keys())[1:] # skip 'self'
    
    kwargs = {}
    
    # Assign known components
    for p in params:
        if p == "plugboard":
            kwargs[p] = plugboard_inst
        elif p == "reflector":
            kwargs[p] = reflector_inst
        elif p == "etw":
            kwargs[p] = etw
        elif p == "auto_increment_rotors":
            kwargs[p] = config["default_auto_increment"]
        elif p.startswith("rotor"):
            # Enigmapython constructors define rotor1=Right(fast), rotor2=Middle, rotor3=Left, etc.
            # The user provides rotors from Left to Right.
            # So rotor1 is the last element in rotor_instances, rotor2 is second to last, etc.
            try:
                # E.g., 'rotor1' -> idx = 1 -> rotor_instances[-1]
                idx = int(p.replace("rotor", ""))
                if 1 <= idx <= len(rotor_instances):
                    kwargs[p] = rotor_instances[-idx]
                else:
                    raise ValueError(f"Machine {machine_model} expects more rotors than provided.")
            except ValueError:
                pass # Not a numbered rotor

    # Instantiate
    machine = machine_cls(**kwargs)
    
    # 6. Process message
    # enigmapython typically uses input_string
    return machine.input_string(message)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Enigma MCP Server")
    parser.add_argument("--transport", choices=["stdio", "sse"], default="stdio", help="Transport protocol (stdio or sse)")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind for SSE")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind for SSE")
    args = parser.parse_args()
    
    if args.transport == "sse":
        mcp.run(transport="sse", host=args.host, port=args.port)
    else:
        mcp.run()
