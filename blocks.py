
"""File containing all the blocks"""
import re

# https://github.com/scratchfoundation/scratch-parser/blob/d48cf549388f2c0fb7f330e8942c7b299ef4f9a9/lib/sb3_definitions.json
# https://github.com/scratchfoundation/scratch-vm/blob/7419b10eb766574c84b9f33a422614b5eb1fd877/src/serialization/sb3.js#L62
"""
'none': [1, None], # ??
'substack': [2, None], # substack and boolean are separate because the block handling is different
'boolean': [2, None],
'number': [4, '0'],
'positive_number': [5, '0'], # time
'positive_integer': [6, ''], # count
'layer': [7, ''], # layers
'list_item': [7, ''],
'direction': [8, '90'], # set dir
'color': [9, '#000000'],
'text': [10, ''],
'broadcast': [11, None],
'variable_reporter': [12, None],
'list_reporter': [13, None],
"""


KEY_OPTIONS = ['space','up arrow','down arrow','right arrow','left arrow','enter','shift','any','!','"','#','$','%','&','\'','(',')','*','+',',','-','.','/','0','1','2','3','4','5','6','7','8','9',':',';','<','=','>','?','@','[','\\',']','^','_','`','a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','{','|','}','~']
EFFECTS = ['COLOR', 'FISHEYE', 'WHIRL', 'PIXELATE', 'MOSAIC', 'BRIGHTNESS', 'GHOST']
SOUND_EFFECTS = ['PITCH', 'PAN']

class Input():
    def __init__(self):
        pass
    
    def to_list(self):
        # this is the common format used so is default
        # TODO account for shadow blocks
        if isinstance(self.block, Block):
            raise Exception('can not convert a Block to a list, it should be converted to a string block id')
        if self.block is None: return [1, [self.enum, self.value]]
        return [3, self.block, [self.enum, self.value]]

    @classmethod
    def from_list(cls, data):
        """Constructor using Scratch JSON input format such as `[3, "a", [4, ""]]`"""
        if data is None: 
            # no data (such as a fallback when no input is found), use default.
            return cls()
        if data[0] == 1:
            return cls(data[1][1])
        elif data[0] == 2:
            return cls(data[1])
        elif data[0] == 3:
            return cls(data[2][1], data[1])

class InputStack(Input):
    def __init__(self, block=None):
        """e.g. if block nesting"""
        self.block = block
        self.enum = 2
    
    def to_list(self):
        return [self.enum, self.block]

class InputBoolean(Input):
    def __init__(self, block=None):
        """e.g. not block"""
        self.block = block
        self.enum = 2
    
    def to_list(self):
        return [self.enum, self.block]

class InputNumber(Input):
    def __init__(self, value='', block=None): # 4 is any number
        """e.g. math operator"""
        self.value = value
        self.block = block
        self.enum = 4


class InputPositiveNumber(Input):
    def __init__(self, value='', block=None): 
        """e.g. seconds, (oddly) not size"""
        self.value = value
        self.block = block
        self.enum = 5

class InputPositiveInteger(Input):
    def __init__(self, value='', block=None): 
        """e.g. repeat count"""
        self.value = value
        self.block = block
        self.enum = 6

class InputInteger(Input):
    def __init__(self, value='', block=None): 
        """e.g. layer, (oddly) list item but not letter number"""
        self.value = value
        self.block = block
        self.enum = 7

class InputAngle(Input):
    def __init__(self, value='', block=None): 
        """e.g. direction"""
        self.value = value
        self.block = block
        self.enum = 8

class InputColor(Input):
    def __init__(self, value='#000000', block=None): 
        self.value = str(value)
        self.block = block
        self.enum = 9
    
    def to_list(self):
        if re.fullmatch(r"^#[a-fA-F0-9]{6}$", self.value) is None:
            raise Exception('Not a correctly formatted color')
        return super().to_list()

class InputText(Input):
    def __init__(self, value='', block=None): 
        """e.g. say block"""
        self.value = str(value)
        self.block = block
        self.enum = 10

class InputBroadcast(Input):
    def __init__(self, value='', block=None): 
        self.value = str(value)
        self.block = block
        self.enum = 11

# if block is actually a variable reporter, it should instead be a list [12, var name, var id]
# list reporter is 13
# but this can be ignored and treated as another block id



class Block():
    """Base block class"""
    def __init__(self):
        # self.shape = None # custom val for operator/stack?
        self.opcode = None
        self.next = None
        self.parent = None
        self.inputs = {}
        self.fields = {}
        self.shadow = False
        #self.topLevel = False # depends on parent being None
        self.x = 0
        self.y = 0
        # mutators?
        

    def copy_parent(self, source_dict:dict):
        """Copy parent data of a block in dict format"""
        self.parent = source_dict['parent']
        self.x = source_dict.get('x', 0)
        self.y = source_dict.get('y', 0)

    def copy_next(self, source_dict:dict):
        """Copy next data of a block in dict format"""
        self.next = source_dict['next']


    def add_input(self, input_type, key:str, value):
        """Register a block input with data. Data must be an input object, the contents of the object may be existing block ids, block objects (blocks to create), or literals."""

        if not isinstance(value, input_type):
            raise Exception('input is not of the correct class')
        if key in self.inputs:
            raise Exception('key already exists')
        
        self.inputs[key] = value

    def add_field(self, key:str, value):
        # fields don't accept blocks
        if key in self.fields:
            raise Exception('key already exists')

        self.fields[key] = [value, None] # no idea what the second item is

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

        return output

    def __str__(self):
        return f"{self.__class__}"



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

class OperatorMathOp(Block):
    def __init__(self, op, num:InputNumber):
        super().__init__()
        self.opcode = 'operator_mathop'
        #self.add_input(InputBoolean, 'OPERAND1', a)
        if op not in ['abs','floor','ceiling','sqrt','sin','cos','tan','asin','acos','atan','ln','log','e ^','10 ^']: raise Exception(f'unknown math op {op}')
        self.add_field('OPERATOR', op)
        self.add_input(InputNumber, 'NUM', num)



class SensingDaysSince2000(Block):
    def __init__(self):
        super().__init__()
        self.opcode = 'sensing_dayssince2000'