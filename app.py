from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# Node structure for AST representation
class Node:
    def __init__(self, node_type, value=None, left=None, right=None):
        self.node_type = node_type  # "operator" or "operand"
        self.value = value          # for operand nodes (e.g., age, salary)
        self.left = left            # left child (Node)
        self.right = right          # right child (Node)

    # Method to serialize the Node object into a dictionary (JSON-compatible)
    def to_dict(self):
        return {
            "node_type": self.node_type,
            "value": self.value,
            "left": self.left.to_dict() if self.left else None,
            "right": self.right.to_dict() if self.right else None
        }

# Function to convert a dictionary back into a Node object
def dict_to_node(node_dict):
    if not node_dict:
        return None
    return Node(
        node_dict["node_type"],
        node_dict.get("value"),
        dict_to_node(node_dict.get("left")),
        dict_to_node(node_dict.get("right"))
    )

# Function to create a rule (parse a string into an AST)
def create_rule(rule_string):
    # This is a placeholder for actual parsing logic
    return Node("operator", "OR",
                Node("operator", "AND",
                     Node("operand", ("age", ">", 30)),
                     Node("operand", ("department", "==", "Sales"))
                ),
                Node("operator", "AND",
                     Node("operand", ("age", "<", 25)),
                     Node("operand", ("department", "==", "Marketing"))
                )
    )

# Function to combine multiple rules into a single AST
def combine_rules(rules):
    if not rules:
        return None
    if len(rules) == 1:
        return create_rule(rules[0])

    root = create_rule(rules[0])
    for rule in rules[1:]:
        root = Node("operator", "OR", root, create_rule(rule))
    
    return root

# Function to evaluate a rule (AST) based on input data
def evaluate_rule(node, data):
    if node.node_type == "operand":
        attr, op, value = node.value
        if op == ">":
            return data[attr] > value
        elif op == "<":
            return data[attr] < value
        elif op == "==":
            return data[attr] == value
        elif op == ">=":
            return data[attr] >= value
        elif op == "<=":
            return data[attr] <= value
    elif node.node_type == "operator":
        if node.value == "AND":
            return evaluate_rule(node.left, data) and evaluate_rule(node.right, data)
        elif node.value == "OR":
            return evaluate_rule(node.left, data) or evaluate_rule(node.right, data)

# API Endpoints
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/create_rule', methods=['POST'])
def create_rule_api():
    rule_string = request.json.get("rule")
    ast = create_rule(rule_string)
    return jsonify({"ast": ast.to_dict()})  # Return serialized AST

@app.route('/combine_rules', methods=['POST'])
def combine_rules_api():
    rules = request.json.get("rules")
    combined_ast = combine_rules(rules)
    return jsonify({"combined_ast": combined_ast.to_dict()})  # Return serialized AST

@app.route('/evaluate_rule', methods=['POST'])
def evaluate_rule_api():
    ast = request.json.get("ast")  # JSON input from the frontend
    data = request.json.get("data")

    # Debugging output to ensure the incoming data is structured correctly
    print("Received AST:", ast)
    print("Received Data:", data)

    # Error handling for AST conversion
    if not isinstance(ast, dict):
        print("AST is not a dictionary")
        return jsonify({"error": "Invalid AST format: should be a dictionary."}), 400
    
    try:
        # Convert AST back to Node objects
        root_node = dict_to_node(ast)  # Convert the JSON AST back to Node
        
        # Debugging: Print the structure of the root node
        print("Root Node Structure:", root_node.to_dict())

        # Evaluate the rule using the Node structure
        result = evaluate_rule(root_node, data)
        
        # Return the evaluation result
        return jsonify({"result": result})
    
    except Exception as e:
        print("Error during evaluation:", e)
        return jsonify({"error": "Evaluation error: " + str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
