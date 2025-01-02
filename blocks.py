"""File containing all the blocks"""
import re

# https://github.com/scratchfoundation/scratch-parser/blob/d48cf549388f2c0fb7f330e8942c7b299ef4f9a9/lib/sb3_definitions.json
# https://github.com/scratchfoundation/scratch-vm/blob/7419b10eb766574c84b9f33a422614b5eb1fd877/src/serialization/sb3.js#L62

KEY_OPTIONS = ['space','up arrow','down arrow','right arrow','left arrow','enter','shift','any','!','"','#','$','%','&','\'','(',')','*','+',',','-','.','/','0','1','2','3','4','5','6','7','8','9',':',';','<','=','>','?','@','[','\\',']','^','_','`','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','{','|','}','~']
EFFECTS = ['COLOR', 'FISHEYE', 'WHIRL', 'PIXELATE', 'MOSAIC', 'BRIGHTNESS', 'GHOST']
SOUND_EFFECTS = ['PITCH', 'PAN']

class Input():
    def __init__(self, shadow_enum, shadow_value, block=None):
        self.shadow_enum = shadow_enum # None if shadow value references a shadow block (not user input)
        self.shadow_value = shadow_value # allowed to be any value
        self.block = block # the block that can be inserted manually
    
    def to_list(self):
        """Convert to list format such as `[3, "a", [4, ""]]`"""
        if isinstance(self.block, Block):
            raise Exception('block is a Block, it must be converted into a string ID first')
        if isinstance(self.shadow_value, Block):
            raise Exception('shadow_value is a Block, it must be converted into a string ID first')
        
        if self.shadow_enum is None: 
            shadow_combined = self.shadow_value # None means block reference
        else:
            shadow_combined = [self.shadow_enum, self.shadow_value] # literal value with enum specifying type

        if shadow_combined is None: 
            return [2, self.block] # inserted block but no shadow (empty bool input)
        if self.block is None: 
            return [1, shadow_combined] # no block, use shadow only (shadow block or user input)
        
        if self.shadow_enum is not None and self.shadow_value is None:
            raise Exception('non-null value is required for non-block shadows')

        return [3, self.block, shadow_combined] # inserted block with shadow hidden underneath

    def has_inserted_block(self):
        """True if a manually inserted (non-shadow) block exists"""
        return self.block is not None
    
    def has_shadow_block(self):
        """True if a shadow block exists (is referenced to by id)."""
        return self.shadow_enum is None and self.shadow_value is not None
    
    def is_completely_empty(self):
        """True if the input has no block at all (not even shadow block), such as an empty boolean input or empty stack input"""
        return self.block is None and self.shadow_enum is None and self.shadow_value is None


    def __str__(self):
        return f"{self.__class__.__name__}({self.shadow_enum} {self.shadow_value} {self.block})"

    @classmethod
    def from_object(cls, input_object):
        """Copy data from another input. No data validation."""
        new_input_object = cls()
        new_input_object.shadow_enum = input_object.shadow_enum
        new_input_object.shadow_value = input_object.shadow_value
        new_input_object.block = input_object.block

        return new_input_object

    @classmethod
    def from_list(cls, data):
        """Constructor using Scratch JSON input format such as `[3, "a", [4, ""]]`. Using this rather than parse_list() ensures the object is of the expected type."""
        
        if data is None: 
            return cls() # no data (such as a fallback when no input is found), use default.

        parsed_input = parse_list(data)
        
        # convert to correct class
        new_input_object = cls()
        if not(new_input_object.shadow_enum is not None and parsed_input.shadow_value is None):
            # do not copy if the enum is not none AND shadow value is none
            new_input_object.shadow_value = parsed_input.shadow_value
        new_input_object.block = parsed_input.block
        return new_input_object


class InputStack(Input):
    def __init__(self, shadow_value=None, block=None):
        """e.g. if block nesting"""
        self.shadow_enum = None
        self.shadow_value = shadow_value
        self.block = block

class InputBoolean(Input):
    def __init__(self, shadow_value=None, block=None):
        """e.g. not block"""
        self.shadow_enum = None
        self.shadow_value = shadow_value
        self.block = block

class InputReporter(Input):
    def __init__(self, shadow_value=None, block=None):
        """specifically for inputs with shadow dropdown such as key press"""
        self.shadow_enum = None
        self.shadow_value = shadow_value
        self.block = block

class InputNumber(Input):
    def __init__(self, value='', block=None): # 4 is any number
        """e.g. math operator"""
        self.shadow_enum = 4
        self.shadow_value = value
        self.block = block

class InputPositiveNumber(Input):
    def __init__(self, value='', block=None): 
        """e.g. seconds, (oddly) not size"""
        self.shadow_enum = 5
        self.shadow_value = value
        self.block = block

class InputPositiveInteger(Input):
    def __init__(self, value='', block=None): 
        """e.g. repeat count"""
        self.shadow_enum = 6
        self.shadow_value = value
        self.block = block

class InputInteger(Input):
    def __init__(self, value='', block=None): 
        """e.g. layer, (oddly) list item but not letter number"""
        self.shadow_enum = 7
        self.shadow_value = value
        self.block = block

class InputAngle(Input):
    def __init__(self, value='', block=None): 
        """e.g. direction"""
        self.shadow_enum = 8
        self.shadow_value = value
        self.block = block

class InputColor(Input):
    def __init__(self, value='#000000', block=None): 
        self.shadow_enum = 9
        self.shadow_value = str(value)
        self.block = block
    
    def to_list(self):
        if re.fullmatch(r"^#[a-fA-F0-9]{6}$", self.shadow_value) is None:
            raise Exception('Not a correctly formatted color')
        return super().to_list()

class InputText(Input):
    def __init__(self, value='', block=None): 
        """e.g. say block"""
        self.shadow_enum = 10
        self.shadow_value = str(value)
        self.block = block

class InputBroadcast(Input):
    def __init__(self, value='', block=None): 
        self.shadow_enum = 11
        self.shadow_value = str(value)
        self.block = block

# if block is actually a variable reporter, it should instead be a list [12, var name, var id]
# list reporter is 13
# but this can be ignored and treated as another block id


INPUT_CLASSES = {
    4: InputNumber,
    5: InputPositiveNumber,
    6: InputPositiveInteger,
    7: InputInteger,
    8: InputAngle,
    9: InputColor,
    10: InputText,
    11: InputBroadcast,
}


def parse_list(data:list) -> Input:
    """Convert a Scratch JSON input such as `[3, "a", [4, ""]]` to Input object"""
    
    """
    1 = use the shadow data, e.g. the stuff typed directly into the block
    2 = nothing in the input, most of these are boolean inputs but it applies to all input types
    3 = theres a shadow that could have data, but something else (e.g. a variable) is on top of it and should be used
    """
    if data is None: 
        return Input(None, None, None)
    
    shadow = None
    block = None
    if data[0] == 1: # use shadow
        shadow = data[1]
    elif data[0] == 2: # input without a shadow
        block = data[1] 
    elif data[0] == 3: # block and shadow
        block = data[1]
        shadow = data[2]
    else:
        raise Exception('unknown id')
    
    if shadow is None:
        shadow_enum = None
        shadow_value = None
    elif isinstance(shadow, list):
        shadow_enum = shadow[0]
        shadow_value = shadow[1]
    else: # is block such as [1, "e"]
        shadow_enum = None
        shadow_value = shadow
    
    # Construct relevant input:
    if shadow_enum in INPUT_CLASSES:
        return INPUT_CLASSES[shadow_enum](shadow_value, block) # constructor of a specific shadow type
    
    return Input(shadow_enum, shadow_value, block) # generic block input
    


class Block():
    """Base block class"""
    def __init__(self):
        self.opcode = None
        self.next = None
        self.parent = None
        self.inputs = {}
        self.fields = {}
        self.shadow = False
        #self.topLevel = False # depends on parent being None
        self.x = 0
        self.y = 0
        self.mutation = {}
        

    def copy_parent(self, source_dict:dict):
        """Copy parent data of a block in dict format. Includes `parent`, `x`, and `y` keys."""
        self.parent = source_dict['parent']
        self.x = source_dict.get('x', 0)
        self.y = source_dict.get('y', 0)

    def copy_next(self, source_dict:dict):
        """Copy `next` data of a block in dict format"""
        self.next = source_dict['next']


    def add_input(self, input_type, key:str, value):
        """Register a block input with data. Data must be an input object, the contents of the object may be existing block ids, block objects (blocks to create), or literals."""

        if not isinstance(value, input_type):
            raise Exception(f'input {value} is not of the correct class {input_type}')
        if key in self.inputs:
            raise Exception('key already exists')
        
        self.inputs[key] = value

    def add_field(self, key:str, value):
        # fields don't accept blocks
        if key in self.fields:
            raise Exception('key already exists')

        if not isinstance(value, list):
            value = [value, None] # the field is always formatted as a 2-item list

        self.fields[key] = value

    def to_dict(self):
        """Create a dict representation of a block. The id of itself is not handled here."""

        converted_inputs = {}
        for key, input in self.inputs.items():
            if isinstance(input.block, Block):
                raise Exception(f'input contains a block (so cannot be converted to a dict): {input.block}')
            
            converted_inputs[key] = input.to_list()

        output = {
            "opcode": self.opcode,
            "next": self.next,
            "parent": self.parent,
            "inputs": converted_inputs,
            "fields": self.fields,
            "shadow": self.shadow,
            "topLevel": self.parent is None
        }

        if self.parent is None:
            output['x'] = self.x
            output['y'] = self.y

        if self.mutation:
            output['mutation'] = self.mutation

        return output

    def __str__(self):
        return f"{self.__class__}"




class EventWhenKeyPressed(Block):
    def __init__(self, keyoption:str):
        super().__init__()
        if keyoption not in KEY_OPTIONS: print(f'unknown key {keyoption}')
        self.opcode = 'event_whenkeypressed'
        self.add_field('KEY_OPTION', keyoption)

class EventWhenGreaterThan(Block):
    def __init__(self, variable:str, value:InputNumber):
        super().__init__()
        self.opcode = 'event_whengreaterthan'
        if variable not in ['LOUDNESS', 'TIMER']: raise Exception(f'unknown variable {variable}')
        self.add_field('WHENGREATERTHANMENU', variable)
        self.add_input(InputNumber, 'VALUE', value)


class MotionGoToXY(Block):
    def __init__(self, x:InputNumber, y:InputNumber):
        super().__init__()
        self.opcode = 'motion_gotoxy'
        self.add_input(InputNumber, 'X', x)
        self.add_input(InputNumber, 'Y', y)

class MotionChangeXBy(Block):
    def __init__(self, dx:InputNumber):
        super().__init__()
        self.opcode = 'motion_changexby'
        self.add_input(InputNumber, 'DX', dx)

class MotionChangeYBy(Block):
    def __init__(self, dy:InputNumber):
        super().__init__()
        self.opcode = 'motion_changexby'
        self.add_input(InputNumber, 'DY', dy)

class MotionXPosition(Block):
    def __init__(self):
        super().__init__()
        self.opcode = 'motion_xposition'

class MotionYPosition(Block):
    def __init__(self):
        super().__init__()
        self.opcode = 'motion_yposition'

class MotionPointInDirection(Block):
    def __init__(self, direction:InputAngle):
        super().__init__()
        self.opcode = 'motion_pointindirection'
        self.add_input(InputAngle, 'DIRECTION', direction)

class MotionDirection(Block):
    def __init__(self):
        super().__init__()
        self.opcode = 'motion_direction'


class ControlIf(Block):
    def __init__(self, condition:InputBoolean, substack:InputStack):
        super().__init__()
        self.opcode = 'control_if'
        self.add_input(InputBoolean, 'CONDITION', condition)
        self.add_input(InputStack, 'SUBSTACK', substack)

class ControlIfElse(Block):
    def __init__(self, condition:InputBoolean, substack_true:InputStack, substack_false:InputStack):
        super().__init__()
        self.opcode = 'control_if_else'
        self.add_input(InputBoolean, 'CONDITION', condition)
        self.add_input(InputStack, 'SUBSTACK', substack_true)
        self.add_input(InputStack, 'SUBSTACK2', substack_false)


class SensingKeyPressed(Block):
    def __init__(self, a:InputReporter):
        super().__init__()
        self.opcode = 'sensing_keypressed'
        self.add_input(InputReporter, 'KEY_OPTION', a)

class SensingKeyOptions(Block):
    def __init__(self, keyoption:str):
        super().__init__()
        if keyoption not in KEY_OPTIONS: print(f'unknown key {keyoption}')
        self.opcode = 'sensing_keyoptions'
        self.shadow = True
        self.add_field('KEY_OPTION', keyoption)


class SensingDaysSince2000(Block):
    def __init__(self):
        super().__init__()
        self.opcode = 'sensing_dayssince2000'


class OperatorAdd(Block):
    def __init__(self, a:InputNumber, b:InputNumber):
        super().__init__()
        self.opcode = 'operator_add'
        self.add_input(InputNumber, 'NUM1', a)
        self.add_input(InputNumber, 'NUM2', b)

class OperatorSubtract(Block):
    def __init__(self, a:InputNumber, b:InputNumber):
        super().__init__()
        self.opcode = 'operator_subtract'
        self.add_input(InputNumber, 'NUM1', a)
        self.add_input(InputNumber, 'NUM2', b)

class OperatorMultiply(Block):
    def __init__(self, a:InputNumber, b:InputNumber):
        super().__init__()
        self.opcode = 'operator_multiply'
        self.add_input(InputNumber, 'NUM1', a)
        self.add_input(InputNumber, 'NUM2', b)

class OperatorDivide(Block):
    def __init__(self, a:InputNumber, b:InputNumber):
        super().__init__()
        self.opcode = 'operator_divide'
        self.add_input(InputNumber, 'NUM1', a)
        self.add_input(InputNumber, 'NUM2', b)

class OperatorMod(Block):
    def __init__(self, a:InputNumber, b:InputNumber):
        super().__init__()
        self.opcode = 'operator_mod'
        self.add_input(InputNumber, 'NUM1', a)
        self.add_input(InputNumber, 'NUM2', b)

class OperatorRound(Block):
    def __init__(self, a:InputNumber):
        super().__init__()
        self.opcode = 'operator_round'
        self.add_input(InputNumber, 'NUM', a)

class OperatorLessThan(Block):
    def __init__(self, a:InputText, b:InputText):
        super().__init__()
        self.opcode = 'operator_lt'
        self.add_input(InputText, 'OPERAND1', a)
        self.add_input(InputText, 'OPERAND2', b)

class OperatorGreaterThan(Block):
    def __init__(self, a:InputText, b:InputText):
        super().__init__()
        self.opcode = 'operator_gt'
        self.add_input(InputText, 'OPERAND1', a)
        self.add_input(InputText, 'OPERAND2', b)

class OperatorEquals(Block):
    def __init__(self, a:InputText, b:InputText):
        super().__init__()
        self.opcode = 'operator_equals'
        self.add_input(InputText, 'OPERAND1', a)
        self.add_input(InputText, 'OPERAND2', b)

class OperatorAnd(Block):
    def __init__(self, a:InputBoolean, b:InputBoolean):
        super().__init__()
        self.opcode = 'operator_and'
        self.add_input(InputBoolean, 'OPERAND1', a)
        self.add_input(InputBoolean, 'OPERAND2', b)

class OperatorOr(Block):
    def __init__(self, a:InputBoolean, b:InputBoolean):
        super().__init__()
        self.opcode = 'operator_or'
        self.add_input(InputBoolean, 'OPERAND1', a)
        self.add_input(InputBoolean, 'OPERAND2', b)

class OperatorNot(Block):
    def __init__(self, a:InputBoolean):
        super().__init__()
        self.opcode = 'operator_not'
        self.add_input(InputBoolean, 'OPERAND', a)

class OperatorJoin(Block):
    def __init__(self, a:InputText, b:InputText):
        super().__init__()
        self.opcode = 'operator_join'
        self.add_input(InputText, 'STRING1', a)
        self.add_input(InputText, 'STRING2', b)

class OperatorMathOp(Block):
    def __init__(self, op, num:InputNumber):
        super().__init__()
        self.opcode = 'operator_mathop'
        if op not in ['abs','floor','ceiling','sqrt','sin','cos','tan','asin','acos','atan','ln','log','e ^','10 ^']: raise Exception(f'unknown math op {op}')
        self.add_field('OPERATOR', op)
        self.add_input(InputNumber, 'NUM', num)

class OperatorRandom(Block):
    def __init__(self, a:InputNumber, b:InputNumber):
        super().__init__()
        self.opcode = 'operator_random'
        self.add_input(InputNumber, 'FROM', a)
        self.add_input(InputNumber, 'TO', b)


class DataSetVariableTo(Block):
    def __init__(self, variable_name:str, variable_id:str, value:InputText):
        super().__init__()
        self.opcode = 'data_setvariableto'
        self.add_field('VARIABLE', [variable_name, variable_id])
        self.add_input(InputText, 'VALUE', value)

class DataChangeVariableBy(Block):
    def __init__(self, variable_name:str, variable_id:str, value:InputNumber):
        super().__init__()
        self.opcode = 'data_changevariableby'
        self.add_field('VARIABLE', [variable_name, variable_id])
        self.add_input(InputNumber, 'VALUE', value)


# 'data_lengthoflist': BlockData('reporter', [Field('LIST', format='list')]),

class DataLengthOfList(Block):
    def __init__(self, list_name:str, list_id:str):
        super().__init__()
        self.opcode = 'data_lengthoflist'
        self.add_field('LIST', [list_name, list_id])



class ProceduresCall(Block):
    def __init__(self):
        super().__init__()
        self.opcode = 'procedures_call'
        #self.mutation = mutation
