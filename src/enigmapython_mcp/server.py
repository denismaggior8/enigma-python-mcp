import importlib
from mcp.server.fastmcp import FastMCP


#
#
# If we ever add a new historical machine model to the core enigmapython library, we must remember to update three specific places in this MCP server:
# 
# MODELS_CONFIG Dictionary: Add the new model class and default ETW.
# Sanitization Maps: Ensure the new reflector types are added to KNOWN_REFLECTORS.
# Pydantic Docstrings/Fields: Append the exact strings for the new model, its rotors, and its reflectors to the Field descriptions so the LLM is explicitly aware of them.
# 
# 

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
    rotor_type: str = Field(description="Exact Rotor identifier. Valid options: 'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'Beta', 'Gamma'.")
    ring_setting: int = Field(default=0, description="Ring setting (0-25).")
    initial_position: Union[int, str] = Field(default=0, description="Initial position (0-25 or A-Z).")

class ReflectorConfig(BaseModel):
    reflector_type: str = Field(description="Exact Reflector identifier. Valid options: 'UKWA', 'UKWB', 'UKWC', 'UKWBThin', 'UKWCThin', 'UKW_EnigmaCommercial', 'UKW_EnigmaINorway', 'UKW_EnigmaISonder', 'UKW_EnigmaB_A133'.")
    ring_setting: int = Field(default=0, description="Ring setting (0-25). Only applicable for settable/rotating reflectors.")
    initial_position: Union[int, str] = Field(default=0, description="Initial position (0-25 or A-Z). Only applicable for rotating reflectors.")

@mcp.tool()
def encrypt_message(
    machine_model: str,
    message: Union[str, int],
    rotors: List[RotorConfig],
    reflector: ReflectorConfig,
    plugboard_pairs: Dict[str, str] = None
) -> str:
    """
    Encrypt or decrypt a message using a specified Enigma machine configuration.
    
    Args:
        machine_model: Exact machine model name. MUST be one of: 'M3', 'M4', 'I', 'I_Norway', 'I_Sondermaschine', 'K', 'K_Swiss', 'D', 'Z', 'B_A133'. Do not add 'Enigma' prefix.
        message: The plaintext or ciphertext to process. Can be string or int.
        rotors: List of RotorConfig objects. MUST be ordered exactly as: [Fastest/Rightmost, Middle, Slowest/Leftmost, Greek (if M4)].
        reflector: The ReflectorConfig object.
        plugboard_pairs: Optional dict for plugboard connections (e.g. {"A": "B", "C": "D"}). Ignored if the machine has no plugboard.
    """
    # Map user input flexibly to known models (e.g. "Enigma I-Norway" -> "I_Norway")
    model_key_map = {k.lower().replace("_", "").replace("-", "").replace(" ", ""): k for k in MODELS_CONFIG.keys()}
    mod_clean = machine_model.lower().replace("enigma", "").replace("_", "").replace("-", "").replace(" ", "")
    
    if mod_clean not in model_key_map:
        raise ValueError(f"Unsupported machine model: {machine_model}")
        
    actual_model = model_key_map[mod_clean]
    config = MODELS_CONFIG[actual_model]
    prefix = config["cls"] 
    
    # 1. Initialize ETW
    etw_cls = get_class(config["etw"])
    etw = etw_cls()
    
    # 2. Initialize Reflector
    # Sanitize common LLM formatting mistakes (e.g. "B-Thin Reflector" -> "BTHIN")
    ref_raw = reflector.reflector_type
    ref_clean = ref_raw.upper().replace("REFLECTOR", "").replace("UKW", "").replace("-", "").replace(" ", "").replace("_", "")
    
    # Map cleaned variations to actual class names
    KNOWN_REFLECTORS = [
        "UKWA", "UKWB", "UKWC", "UKWBThin", "UKWCThin",
        "UKW_EnigmaCommercial", "UKW_EnigmaINorway", "UKW_EnigmaISonder", "UKW_EnigmaB_A133"
    ]
    ref_key_map = {k.upper().replace("UKW", "").replace("_", "").replace("-", "").replace(" ", ""): k for k in KNOWN_REFLECTORS}
    
    if ref_clean in ref_key_map:
        ref_type = ref_key_map[ref_clean]
    else: 
        ref_type = ref_raw # Fallback to exactly what the user passed
        
    reflector_cls_name = f"Reflector{ref_type}"
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
        # Sanitize rotor type casing and common prefixes (e.g. "Rotor-I" -> "I", "beta" -> "Beta")
        r_type = r_conf.rotor_type.upper().replace("ROTOR", "").replace("-", "").replace(" ", "").replace("_", "")
        if r_type == "BETA": r_type = "Beta"
        elif r_type == "GAMMA": r_type = "Gamma"
        
        r_cls_name = f"{prefix}Rotor{r_type}"
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
            try:
                idx = int(p.replace("rotor", "")) - 1
                if 0 <= idx < len(rotor_instances):
                    kwargs[p] = rotor_instances[idx]
                else:
                    raise ValueError(f"Machine {machine_model} expects more rotors than provided.")
            except ValueError:
                pass # Not a numbered rotor

    # Instantiate
    machine = machine_cls(**kwargs)
    
    # 6. Process message
    # enigmapython typically uses input_string
    message_str = str(message)
    try:
        return machine.input_string(message_str)
    except ValueError as e:
        error_msg = str(e)
        if "not in list" in error_msg:
            # Give the LLM a highly actionable error so it can self-correct
            raise ValueError(
                f"Invalid character error: {error_msg}. "
                "Enigma machines DO NOT support spaces, punctuation, or literal quotes in the message. "
                "Please strip all unsupported characters and pass only the raw letters/numbers."
            )
        raise

def main():
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

if __name__ == "__main__":
    main()
