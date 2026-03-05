import json
import os

questions = [
    # --- REACT (Frontend) ---
    {
        "domain": "frontend",
        "category": "technical",
        "topic": "React",
        "difficulty_level": 2,
        "primary_skill": "State Management",
        "secondary_skills": ["useState", "Props"],
        "question_text": "What is the difference between state and props in React?",
        "expected_concepts": ["State is local", "Props are passed down", "State is mutable", "Props are read-only"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["State is local/mutable", "Props are passed down/read-only"],
            "supporting_details": ["Component re-renders when state changes"],
            "advanced_knowledge": ["Unidirectional data flow"]
        }
    },
    {
        "domain": "frontend",
        "category": "technical",
        "topic": "React",
        "difficulty_level": 3,
        "primary_skill": "Component Lifecycle",
        "secondary_skills": ["useEffect"],
        "question_text": "How do you handle side effects in a functional React component?",
        "expected_concepts": ["useEffect hook", "Dependency array", "Cleanup function"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["useEffect hook", "Dependency array"],
            "supporting_details": ["Cleanup function for preventing memory leaks"],
            "advanced_knowledge": ["Difference between empty array and no array"]
        }
    },
    {
        "domain": "frontend",
        "category": "technical",
        "topic": "React",
        "difficulty_level": 3,
        "primary_skill": "Context API",
        "secondary_skills": ["Prop Drilling", "Global State"],
        "question_text": "What is prop drilling and how does Context API solve it?",
        "expected_concepts": ["Passing props deeply", "Context API creates global variables", "Provider and Consumer"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["Passing props deeply", "Context avoids intermediate props"],
            "supporting_details": ["Provider wrapping", "useContext hook"],
            "advanced_knowledge": ["Performance implications of Context"]
        }
    },
    {
        "domain": "frontend",
        "category": "technical",
        "topic": "React",
        "difficulty_level": 4,
        "primary_skill": "Performance Optimization",
        "secondary_skills": ["useMemo", "useCallback"],
        "question_text": "When should you use useMemo and useCallback?",
        "expected_concepts": ["useMemo memoizes values", "useCallback memoizes functions", "Prevents unnecessary re-renders"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["useMemo for values", "useCallback for functions"],
            "supporting_details": ["Reference equality in dependency arrays"],
            "advanced_knowledge": ["Overusing them can degrade performance"]
        }
    },
    {
        "domain": "frontend",
        "category": "technical",
        "topic": "React",
        "difficulty_level": 5,
        "primary_skill": "Advanced State",
        "secondary_skills": ["Redux", "Zustand"],
        "question_text": "How does Redux differ from the native Context API in terms of rendering performance?",
        "expected_concepts": ["Context triggers re-render for all consumers", "Redux uses selectors", "Bailout renders"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["Context re-renders all consumers on change", "Redux allows specific state selection"],
            "supporting_details": ["useSelector in Redux"],
            "advanced_knowledge": ["Context is not meant for high-frequency updates"]
        }
    },
    {
        "domain": "frontend",
        "category": "technical",
        "topic": "React",
        "difficulty_level": 4,
        "primary_skill": "Custom Hooks",
        "secondary_skills": ["Reusability", "Abstraction"],
        "question_text": "What is a custom hook in React and why would you create one?",
        "expected_concepts": ["Extracting component logic", "Starts with 'use'", "Shares logic, not state"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["Extracting reusable logic", "Must start with use"],
            "supporting_details": ["Keeps components clean"],
            "advanced_knowledge": ["Custom hooks share stateful logic, not the state itself"]
        }
    },

    # --- NODE.JS (Backend) ---
    {
        "domain": "backend",
        "category": "technical",
        "topic": "Node.js",
        "difficulty_level": 2,
        "primary_skill": "Event Loop",
        "secondary_skills": ["Asynchronous I/O"],
        "question_text": "Explain the concept of non-blocking I/O in Node.js.",
        "expected_concepts": ["Single-threaded", "Event loop offloads tasks", "Callbacks/Promises"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["Single thread for requests", "Event loop handles asynchronous operations"],
            "supporting_details": ["Libuv background workers"],
            "advanced_knowledge": ["Blocking the event loop"]
        }
    },
    {
        "domain": "backend",
        "category": "technical",
        "topic": "Node.js",
        "difficulty_level": 3,
        "primary_skill": "Express Middleware",
        "secondary_skills": ["Request Pipeline"],
        "question_text": "How does middleware work in an Express.js application?",
        "expected_concepts": ["Functions with access to req, res, next", "next() to proceed", "Error handlers"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["Access to request and response", "Calling next()"],
            "supporting_details": ["Order of execution matters"],
            "advanced_knowledge": ["Error handling middleware signature (4 arguments)"]
        }
    },
    {
        "domain": "backend",
        "category": "technical",
        "topic": "Node.js",
        "difficulty_level": 4,
        "primary_skill": "Streams",
        "secondary_skills": ["Memory Management", "File I/O"],
        "question_text": "What are Streams in Node.js and when would you use them?",
        "expected_concepts": ["Handling large data", "Processing chunks without full memory loading", "Readable, Writable, Duplex"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["Processing data in chunks", "Prevents memory overflow"],
            "supporting_details": ["Types of streams (Readable, Writable)"],
            "advanced_knowledge": ["Piping streams (pipe())"]
        }
    },
    {
        "domain": "backend",
        "category": "technical",
        "topic": "Node.js",
        "difficulty_level": 5,
        "primary_skill": "Concurrency",
        "secondary_skills": ["Worker Threads", "Cluster"],
        "question_text": "How would you handle heavy CPU-intensive tasks in a Node.js application?",
        "expected_concepts": ["Worker Threads for parallel JS", "Child Processes", "Offloading from main thread"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["Worker threads", "Offloading CPU tasks to avoid blocking the event loop"],
            "supporting_details": ["Cluster module for process scaling"],
            "advanced_knowledge": ["Thread pools vs independent processes"]
        }
    },
    {
        "domain": "backend",
        "category": "technical",
        "topic": "Node.js",
        "difficulty_level": 3,
        "primary_skill": "Event Emitter",
        "secondary_skills": ["Pub/Sub Pattern"],
        "question_text": "Explain the EventEmitter class in Node.js.",
        "expected_concepts": ["Publish/Subscribe model", "on() to listen, emit() to trigger", "Used internally by streams/http"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["Emitting and listening to events", "on and emit methods"],
            "supporting_details": ["Memory leaks with too many listeners"],
            "advanced_knowledge": ["Synchronous nature of default EventEmitter callbacks"]
        }
    },
    {
        "domain": "backend",
        "category": "technical",
        "topic": "Node.js",
        "difficulty_level": 4,
        "primary_skill": "Promises/Async Await",
        "secondary_skills": ["Event Loop Phases"],
        "question_text": "What is the difference between setImmediate() and setTimeout(fn, 0)?",
        "expected_concepts": ["Timer vs Check phase of event loop", "Execution order within I/O cycles"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["Different phases of the event loop", "setTimeout is timer, setImmediate is check"],
            "supporting_details": ["Non-deterministic order in main module"],
            "advanced_knowledge": ["Deterministic order inside I/O callbacks (setImmediate always first)"]
        }
    },

    # --- PYTHON (Backend) ---
    {
        "domain": "backend",
        "category": "technical",
        "topic": "Python",
        "difficulty_level": 2,
        "primary_skill": "Data Types",
        "secondary_skills": ["Lists", "Dictionaries"],
        "question_text": "What is the difference between a list and a dictionary in Python regarding lookups?",
        "expected_concepts": ["Lists are O(n)", "Dicts are O(1) average", "Dicts use hash tables"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["List lookup is O(n), Dict is O(1)"],
            "supporting_details": ["Dictionaries map keys to values via hashing"],
            "advanced_knowledge": ["Hash collisions"]
        }
    },
    {
        "domain": "backend",
        "category": "technical",
        "topic": "Python",
        "difficulty_level": 3,
        "primary_skill": "Decorators",
        "secondary_skills": ["Higher-Order Functions"],
        "question_text": "What is a decorator in Python and how does it work?",
        "expected_concepts": ["Function that wraps another function", "Takes a function as argument", "@ syntax"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["Modifies behavior of a function without changing its code", "Higher-order functions"],
            "supporting_details": ["Wrapper functions", "*args and **kwargs"],
            "advanced_knowledge": ["functools.wraps preserving metadata"]
        }
    },
    {
        "domain": "backend",
        "category": "technical",
        "topic": "Python",
        "difficulty_level": 4,
        "primary_skill": "Generators",
        "secondary_skills": ["Iterators", "Memory Management"],
        "question_text": "What are generators in Python and why use them over lists?",
        "expected_concepts": ["yield keyword", "Lazy evaluation", "Memory efficiency"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["Uses yield keyword", "Generates values one at a time lazily"],
            "supporting_details": ["Saves memory compared to full lists in memory"],
            "advanced_knowledge": ["State suspension and Iteration protocol (__next__)"]
        }
    },
    {
        "domain": "backend",
        "category": "technical",
        "topic": "Python",
        "difficulty_level": 5,
        "primary_skill": "Concurrency",
        "secondary_skills": ["GIL", "Multiprocessing", "Threading"],
        "question_text": "Explain the Global Interpreter Lock (GIL) in Python and its impact on multi-threading.",
        "expected_concepts": ["Mutex that protects access to Python objects", "Prevents true parallel execution in CPython threads"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["Only one thread executes Python bytecode at a time", "Prevents parallel CPU bound threading"],
            "supporting_details": ["Threading is still good for I/O bound tasks"],
            "advanced_knowledge": ["Overcoming GIL with multiprocessing"]
        }
    },
    {
        "domain": "backend",
        "category": "technical",
        "topic": "Python",
        "difficulty_level": 3,
        "primary_skill": "Memory Management",
        "secondary_skills": ["Garbage Collection"],
        "question_text": "How is memory managed in Python?",
        "expected_concepts": ["Reference counting", "Garbage collector for cyclic references"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["Automated memory management", "Reference counting"],
            "supporting_details": ["Generational garbage collection"],
            "advanced_knowledge": ["Circular reference issues"]
        }
    },
    {
        "domain": "backend",
        "category": "technical",
        "topic": "Python",
        "difficulty_level": 3,
        "primary_skill": "OOP Context",
        "secondary_skills": ["Context Managers"],
        "question_text": "What is a context manager in Python and how is it used?",
        "expected_concepts": ["'with' statement", "Resource management (files, locks)", "__enter__ and __exit__"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["Used with 'with' keyword", "Ensures resources are cleaned up safely"],
            "supporting_details": ["__enter__ and __exit__ dunder methods"],
            "advanced_knowledge": ["contextlib and @contextmanager"]
        }
    },

    # --- JAVASCRIPT (Frontend/Fullstack) ---
    {
        "domain": "frontend",
        "category": "technical",
        "topic": "JavaScript",
        "difficulty_level": 2,
        "primary_skill": "Variable Declaration",
        "secondary_skills": ["Scope", "Hoisting"],
        "question_text": "What is the difference between var, let, and const?",
        "expected_concepts": ["Block scope vs Function scope", "Reassignment rules", "Hoisting"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["let/const are block-scoped, var is function-scoped", "const cannot be reassigned"],
            "supporting_details": ["let/const are not initialized when hoisted (Temporal Dead Zone)"],
            "advanced_knowledge": ["const objects can have mutable properties"]
        }
    },
    {
        "domain": "frontend",
        "category": "technical",
        "topic": "JavaScript",
        "difficulty_level": 3,
        "primary_skill": "Asynchronous JS",
        "secondary_skills": ["Promises", "Callbacks"],
        "question_text": "Explain how Promises differ from Callbacks.",
        "expected_concepts": ["Avoiding callback hell", "Chaining (.then)", "States: Pending, Resolved, Rejected"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["Promises represent future values", "Cleaner syntax than deep callbacks"],
            "supporting_details": ["Three states of a Promise", ".catch() for error handling"],
            "advanced_knowledge": ["Microtasks queue prioritization"]
        }
    },
    {
        "domain": "frontend",
        "category": "technical",
        "topic": "JavaScript",
        "difficulty_level": 4,
        "primary_skill": "Closures",
        "secondary_skills": ["Lexical Scope"],
        "question_text": "What is a closure in JavaScript? Provide a real-world use case.",
        "expected_concepts": ["Function accessing variables from outer scope", "Data privacy", "Currying/Factory functions"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["Inner function remembers outer scope even after execution"],
            "supporting_details": ["Used for data encapsulation / private variables"],
            "advanced_knowledge": ["Memory leak risks with unintentional closures"]
        }
    },
    {
        "domain": "frontend",
        "category": "technical",
        "topic": "JavaScript",
        "difficulty_level": 4,
        "primary_skill": "Event Binding",
        "secondary_skills": ["Event Delegation"],
        "question_text": "What is Event Delegation in JavaScript?",
        "expected_concepts": ["Attaching single listener to parent", "Event bubbling", "Performance benefits for large lists"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["Putting listener on parent instead of many children", "Relies on event bubbling"],
            "supporting_details": ["e.target vs e.currentTarget", "Better memory usage"],
            "advanced_knowledge": ["Events that do not bubble (e.g. focus/blur)"]
        }
    },
    {
        "domain": "frontend",
        "category": "technical",
        "topic": "JavaScript",
        "difficulty_level": 5,
        "primary_skill": "Prototypal Inheritance",
        "secondary_skills": ["Object Oriented JS"],
        "question_text": "How does prototypal inheritance work in JavaScript?",
        "expected_concepts": ["Prototype chain", "Objects linking to other objects", "__proto__ vs prototype"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["Objects inherit properties from prototypes", "Lookup chain continues until null"],
            "supporting_details": ["Object.create()", "Function constructor prototypes"],
            "advanced_knowledge": ["ES6 Classes are syntactic sugar over prototypes"]
        }
    },
    {
        "domain": "frontend",
        "category": "technical",
        "topic": "JavaScript",
        "difficulty_level": 3,
        "primary_skill": "Array Methods",
        "secondary_skills": ["Functional Programming"],
        "question_text": "What is the difference between map() and forEach()?",
        "expected_concepts": ["map returns a new array", "forEach returns undefined", "Immutability vs mutation"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["map() creates a new array", "forEach() is for side effects returning undefined"],
            "supporting_details": ["Chaining methods after map"],
            "advanced_knowledge": ["Difference in performance/allocation"]
        }
    },

    # --- MONGODB (Database) ---
    {
        "domain": "database",
        "category": "technical",
        "topic": "MongoDB",
        "difficulty_level": 2,
        "primary_skill": "Data Modeling",
        "secondary_skills": ["NoSQL"],
        "question_text": "What is the difference between a relational database and a document database like MongoDB?",
        "expected_concepts": ["Tables vs Collections", "Rows vs Documents", "Flexible schema"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["Schema-less / flexible schemas", "JSON/BSON storage"],
            "supporting_details": ["Good for unstructured data"],
            "advanced_knowledge": ["Lack of native multi-document ACID transactions before v4"]
        }
    },
    {
        "domain": "database",
        "category": "technical",
        "topic": "MongoDB",
        "difficulty_level": 3,
        "primary_skill": "Aggregation",
        "secondary_skills": ["Pipelines"],
        "question_text": "Explain how the Aggregation Framework works in MongoDB.",
        "expected_concepts": ["Pipeline stages", "$match, $group, $project", "Data transformation"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["Pipeline of sequential processing stages"],
            "supporting_details": ["Examples of stages like $match for filtering, $group for grouping"],
            "advanced_knowledge": ["Using $match early to use indexes"]
        }
    },
    {
        "domain": "database",
        "category": "technical",
        "topic": "MongoDB",
        "difficulty_level": 5,
        "primary_skill": "Optimization",
        "secondary_skills": ["Indexing", "Explain"],
        "question_text": "How do you optimize slow queries in a large MongoDB collection?",
        "expected_concepts": ["Creating Indexes", ".explain() plans", "Avoiding COLLSCAN", "Covered Queries"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["Adding indexes to queried fields", "Using the query analyzer/explain"],
            "supporting_details": ["Compound indexes and the ESR (Equality, Sort, Range) rule"],
            "advanced_knowledge": ["Covered queries where index satisfies all fields"]
        }
    },
    {
        "domain": "database",
        "category": "technical",
        "topic": "MongoDB",
        "difficulty_level": 4,
        "primary_skill": "Relationships",
        "secondary_skills": ["Embedding vs Referencing"],
        "question_text": "When structuring data in MongoDB, when should you use embedding versus referencing?",
        "expected_concepts": ["1:1 or 1:few favors embedding", "1:many or frequently updated data favors referencing"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["Embedding for data accessed together", "Referencing for unbounded growth arrays"],
            "supporting_details": ["Document size limit (16MB) restriction on embedding"],
            "advanced_knowledge": ["$lookup for performing joins on referenced documents"]
        }
    },
    {
        "domain": "database",
        "category": "technical",
        "topic": "MongoDB",
        "difficulty_level": 4,
        "primary_skill": "High Availability",
        "secondary_skills": ["Replica Sets"],
        "question_text": "What is a Replica Set in MongoDB and why is it used?",
        "expected_concepts": ["Nodes maintaining same data set", "Primary and Secondary nodes", "Failover/Redundancy"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["Group of mongod instances controlling same data", "High availability and failover"],
            "supporting_details": ["Primary receives writes, secondaries replicate oplog"],
            "advanced_knowledge": ["Read preferences and eventual consistency reading from secondaries"]
        }
    },
    {
        "domain": "database",
        "category": "technical",
        "topic": "MongoDB",
        "difficulty_level": 5,
        "primary_skill": "Scaling",
        "secondary_skills": ["Sharding"],
        "question_text": "Explain sharding in MongoDB and how choosing a shard key impacts performance.",
        "expected_concepts": ["Distributing data across machines", "Shard key determines distribution", "Hotspots"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["Horizontal scaling by splitting data", "Shard key dictates chunk distribution"],
            "supporting_details": ["Monotonic keys cause hotspots", "Hashed vs range-based sharding"],
            "advanced_knowledge": ["Impact of scatter-gather queries on un-targeted shards"]
        }
    },

    # --- POSTGRESQL (Database) ---
    {
        "domain": "database",
        "category": "technical",
        "topic": "PostgreSQL",
        "difficulty_level": 2,
        "primary_skill": "Relationships",
        "secondary_skills": ["JOINs", "Foreign Keys"],
        "question_text": "What are the different types of JOIN clauses in SQL?",
        "expected_concepts": ["INNER JOIN", "LEFT/RIGHT OUTER JOIN", "FULL OUTER JOIN"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["INNER JOIN returns matches", "LEFT JOIN returns all from left + matches"],
            "supporting_details": ["FULL OUTER JOIN returns all rows from both if there's a match"],
            "advanced_knowledge": ["CROSS JOIN / Cartesian product"]
        }
    },
    {
        "domain": "database",
        "category": "technical",
        "topic": "PostgreSQL",
        "difficulty_level": 3,
        "primary_skill": "ACID Properties",
        "secondary_skills": ["Transactions"],
        "question_text": "Explain the ACID properties of a database transaction.",
        "expected_concepts": ["Atomicity, Consistency, Isolation, Durability"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["Atomicity (All or nothing)", "Consistency (Valid rules)", "Isolation (Concurrent control)", "Durability (Saved permanently)"],
            "supporting_details": ["BEGIN, COMMIT, ROLLBACK commands"],
            "advanced_knowledge": ["Write-Ahead Logging (WAL) for durability"]
        }
    },
    {
        "domain": "database",
        "category": "technical",
        "topic": "PostgreSQL",
        "difficulty_level": 4,
        "primary_skill": "Performance",
        "secondary_skills": ["Indexing", "B-Tree"],
        "question_text": "What is a database index and how does it speed up queries?",
        "expected_concepts": ["Data structure pointing to records", "B-Tree implementation", "O(log n) lookup"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["Lookup table to find data without full table scan", "Usually B-Tree structure"],
            "supporting_details": ["Trade-off: Slower INSERT/UPDATE operations"],
            "advanced_knowledge": ["Hash indexes or GIN indexes in Postgres"]
        }
    },
    {
        "domain": "database",
        "category": "technical",
        "topic": "PostgreSQL",
        "difficulty_level": 4,
        "primary_skill": "Isolation Levels",
        "secondary_skills": ["Concurrency", "Dirty Reads"],
        "question_text": "What are Transaction Isolation Levels and what problems do they solve?",
        "expected_concepts": ["Read Uncommitted, Read Committed, Repeatable Read, Serializable", "Dirty reads, Non-repeatable reads, Phantom reads"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["Levels determining visibility of concurrent changes"],
            "supporting_details": ["Read Committed is default in Postgres", "Solves dirty reads/phantom reads"],
            "advanced_knowledge": ["MVCC (Multi-Version Concurrency Control) implementation in Postgres"]
        }
    },
    {
        "domain": "database",
        "category": "technical",
        "topic": "PostgreSQL",
        "difficulty_level": 5,
        "primary_skill": "Query Optimization",
        "secondary_skills": ["EXPLAIN ANALYZE"],
        "question_text": "How do you analyze a slow query in PostgreSQL?",
        "expected_concepts": ["EXPLAIN ANALYZE clause", "Sequential scans vs Index scans", "Query planner"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["Using EXPLAIN ANALYZE to view execution plan and times"],
            "supporting_details": ["Looking for Seq Scan (Sequential Scans) bottlenecks"],
            "advanced_knowledge": ["Vacuuming / ANALYZE updating table statistics for the planner"]
        }
    },
    {
        "domain": "database",
        "category": "technical",
        "topic": "PostgreSQL",
        "difficulty_level": 3,
        "primary_skill": "Data Modeling",
        "secondary_skills": ["Normalization"],
        "question_text": "What is database normalization and what are its benefits?",
        "expected_concepts": ["Organizing data to reduce redundancy", "1NF, 2NF, 3NF", "Data integrity"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["Reducing duplicated data", "Splitting tables to ensure single sources of truth"],
            "supporting_details": ["First, Second, and Third Normal Forms"],
            "advanced_knowledge": ["Denormalization for read-heavy performance optimization"]
        }
    },

    # --- SYSTEM DESIGN (Architecture) ---
    {
        "domain": "system_design",
        "category": "system_design",
        "topic": "System Design",
        "difficulty_level": 3,
        "primary_skill": "Load Balancing",
        "secondary_skills": ["Horizontal Scaling"],
        "question_text": "What is a load balancer and what algorithms can it use?",
        "expected_concepts": ["Distributes traffic across servers", "Round Robin", "Least Connections"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["Reverse proxy distributing traffic to backend servers", "Prevents single server overload"],
            "supporting_details": ["Round robin, Least connections routing"],
            "advanced_knowledge": ["Layer 4 (Transport) vs Layer 7 (Application) load balancing"]
        }
    },
    {
        "domain": "system_design",
        "category": "system_design",
        "topic": "System Design",
        "difficulty_level": 3,
        "primary_skill": "Caching",
        "secondary_skills": ["Redis", "Memcached"],
        "question_text": "Why and where would you introduce a caching layer in your system architecture?",
        "expected_concepts": ["Database offloading", "Decreasing latency", "Key-value stores", "Write-through vs Cache-aside"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["Storing frequently accessed data in memory", "Reduces DB load and response time"],
            "supporting_details": ["Redis/Memcached", "Cache invalidation challenges"],
            "advanced_knowledge": ["Cache-aside vs Write-through caching strategies"]
        }
    },
    {
        "domain": "system_design",
        "category": "system_design",
        "topic": "System Design",
        "difficulty_level": 4,
        "primary_skill": "Scaling",
        "secondary_skills": ["Vertical vs Horizontal"],
        "question_text": "Compare vertical scaling vs horizontal scaling.",
        "expected_concepts": ["Adding more power (CPU/RAM) vs Adding more servers", "Horizontal provides redundancy", "Vertical has physical limits"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["Vertical = bigger machine, Horizontal = more machines"],
            "supporting_details": ["Horizontal is harder to build (statelessness), Vertical has a ceiling limit"],
            "advanced_knowledge": ["Horizontal scaling requires load balancers and distributed databases"]
        }
    },
    {
        "domain": "system_design",
        "category": "system_design",
        "topic": "System Design",
        "difficulty_level": 5,
        "primary_skill": "Microservices",
        "secondary_skills": ["Distributed Systems", "Message Brokers"],
        "question_text": "What are the trade-offs of using a Microservices architecture instead of a Monolith?",
        "expected_concepts": ["Independent deployment vs Networking complexity", "Polyglot environments", "Distributed transactions"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["Decoupled scalability but higher operational complexity"],
            "supporting_details": ["Issues with cross-service network latency and debugging"],
            "advanced_knowledge": ["Saga patterns, Distributed Tracing, API Gateways"]
        }
    },
    {
        "domain": "system_design",
        "category": "system_design",
        "topic": "System Design",
        "difficulty_level": 4,
        "primary_skill": "Message Queues",
        "secondary_skills": ["Asynchronous Processing", "RabbitMQ", "Kafka"],
        "question_text": "When would you use a Message Queue like RabbitMQ or Kafka in a system design?",
        "expected_concepts": ["Decoupling services", "Asynchronous background processing", "Spike smoothing / Buffering"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["Offloading heavy tasks from the critical path", "Decoupling systems asynchronously"],
            "supporting_details": ["Handling sudden traffic spikes (buffering)"],
            "advanced_knowledge": ["Exactly-once vs At-least-once delivery guarantees"]
        }
    },
    {
        "domain": "system_design",
        "category": "system_design",
        "topic": "System Design",
        "difficulty_level": 5,
        "primary_skill": "CAP Theorem",
        "secondary_skills": ["Distributed Databases"],
        "question_text": "Explain the CAP theorem in database design.",
        "expected_concepts": ["Consistency, Availability, Partition Tolerance", "Can only choose 2 in a partition"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["Consistency, Availability, Partition tolerance definition", "You can only guarantee two during a network partition"],
            "supporting_details": ["Network partitions (P) are inevitable, so you choose AP or CP"],
            "advanced_knowledge": ["Eventual consistency in AP systems (Cassandra/Dynamo)"]
        }
    },

    # --- HTML / CSS (Frontend) ---
    {
        "domain": "frontend",
        "category": "technical",
        "topic": "HTML/CSS",
        "difficulty_level": 2,
        "primary_skill": "CSS Box Model",
        "secondary_skills": ["Layout"],
        "question_text": "Explain the CSS Box Model.",
        "expected_concepts": ["Content, Padding, Border, Margin", "box-sizing: border-box"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["Elements consist of content, padding, border, and margin"],
            "supporting_details": ["Margin is outside, padding is inside"],
            "advanced_knowledge": ["box-sizing: border-box includes padding in element width"]
        }
    },
    {
        "domain": "frontend",
        "category": "technical",
        "topic": "HTML/CSS",
        "difficulty_level": 2,
        "primary_skill": "Semantic HTML",
        "secondary_skills": ["Accessibility", "SEO"],
        "question_text": "Why is semantic HTML important?",
        "expected_concepts": ["Screen readers/Accessibility", "SEO indexing", "Readability", "<header>, <nav>, <main>"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["Improves accessibility for screen readers", "Better SEO"],
            "supporting_details": ["Using descriptive tags like <article> instead of <div>"],
            "advanced_knowledge": ["ARIA attributes relationship to semantics"]
        }
    },
    {
        "domain": "frontend",
        "category": "technical",
        "topic": "HTML/CSS",
        "difficulty_level": 3,
        "primary_skill": "Flexbox vs Grid",
        "secondary_skills": ["CSS Layout"],
        "question_text": "When should you use CSS Flexbox vs CSS Grid?",
        "expected_concepts": ["Flexbox is 1-Dimensional", "Grid is 2-Dimensional", "Alignment vs Layout"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["Flexbox for 1D (rows or columns)", "Grid for 2D (rows AND columns)"],
            "supporting_details": ["Flexbox mostly for content alignment, Grid for page structure"],
            "advanced_knowledge": ["fr units in Grid and auto-fit/auto-fill"]
        }
    },
    {
        "domain": "frontend",
        "category": "technical",
        "topic": "HTML/CSS",
        "difficulty_level": 3,
        "primary_skill": "CSS Specificity",
        "secondary_skills": ["Cascading"],
        "question_text": "How does CSS Specificity resolve conflicting styles?",
        "expected_concepts": ["Weight of selectors", "Inline > ID > Class > Element", "!important rule"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["IDs beat Classes, Classes beat Tags", "Inline styles override external"],
            "supporting_details": ["The point system calculation"],
            "advanced_knowledge": ["Why using !important is generally bad practice"]
        }
    },
    {
        "domain": "frontend",
        "category": "technical",
        "topic": "HTML/CSS",
        "difficulty_level": 4,
        "primary_skill": "Responsive Design",
        "secondary_skills": ["Media Queries", "Viewports"],
        "question_text": "What strategies do you use to make a website perfectly responsive?",
        "expected_concepts": ["Media queries", "Relative units (rem, vw, %)", "Mobile-first approach", "Fluid typography"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["Media queries (@media)", "Using relative units like %, em, rem, vh, vw"],
            "supporting_details": ["Mobile-first design philosophy"],
            "advanced_knowledge": ["Clamp() function or responsive images via srcset"]
        }
    },
    {
        "domain": "frontend",
        "category": "technical",
        "topic": "HTML/CSS",
        "difficulty_level": 5,
        "primary_skill": "CSS Architecture",
        "secondary_skills": ["BEM", "Tailwind"],
        "question_text": "Discuss the pros and cons of utility-first CSS frameworks like Tailwind compared to traditional CSS methodologies like BEM.",
        "expected_concepts": ["Utility CSS avoids context switching but clutters HTML", "BEM is clean HTML but rigid CSS", "File size differences"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["Tailwind removes need for naming classes, speeds up dev", "BEM creates readable markup and reusable components"],
            "supporting_details": ["Utility CSS results in smaller final CSS bundles due to purging"],
            "advanced_knowledge": ["Component abstraction in Tailwind (@apply)"]
        }
    },

    # --- TYPESCRIPT / GENERAL (Frontend/Backend) ---
    {
        "domain": "fullstack",
        "category": "technical",
        "topic": "TypeScript",
        "difficulty_level": 2,
        "primary_skill": "Type Checking",
        "secondary_skills": ["Static Typing"],
        "question_text": "What is the main benefit of using TypeScript over plain JavaScript?",
        "expected_concepts": ["Static type checking at compile time", "Catches errors before runtime", "IDE autocomplete support"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["Catching errors at compile time instead of runtime", "Static typing"],
            "supporting_details": ["Improves codebase refactoring confidence", "Better IDE autocompletion"],
            "advanced_knowledge": ["TypeScript compiles to plain JS, types don't exist at runtime"]
        }
    },
    {
        "domain": "fullstack",
        "category": "technical",
        "topic": "TypeScript",
        "difficulty_level": 3,
        "primary_skill": "Interfaces vs Types",
        "secondary_skills": ["Type Aliases"],
        "question_text": "What is the difference between an Interface and a Type alias in TypeScript?",
        "expected_concepts": ["Interfaces are extendable via declaration merging", "Types can represent unions/primitives", "Usage preference"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["Types can do unions/intersections, Interfaces are strictly for object shapes"],
            "supporting_details": ["Interfaces support declaration merging (can be re-opened)"],
            "advanced_knowledge": ["Performance differences in complex types"]
        }
    },
    {
        "domain": "fullstack",
        "category": "technical",
        "topic": "TypeScript",
        "difficulty_level": 4,
        "primary_skill": "Generics",
        "secondary_skills": ["Reusable Types"],
        "question_text": "What are Generics in TypeScript and when would you use them?",
        "expected_concepts": ["Types taking parameters", "Building reusable components/functions", "<T> syntax"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["Allow writing reusable functions/classes that work with any type", "Passed as parameters using <T>"],
            "supporting_details": ["Provides type safety without losing information (unlike 'any')"],
            "advanced_knowledge": ["Generic constraints (extends keyword)"]
        }
    },

    # --- DOCKER / DEVOPS (Backend) ---
    {
        "domain": "backend",
        "category": "technical",
        "topic": "Docker",
        "difficulty_level": 2,
        "primary_skill": "Containerization",
        "secondary_skills": ["Images vs Containers"],
        "question_text": "What is the difference between a Docker Image and a Docker Container?",
        "expected_concepts": ["Image is an immutable blueprint", "Container is a running instance of an image"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["Image is a static file/blueprint", "Container is the live running process"],
            "supporting_details": ["Images are built via Dockerfile"],
            "advanced_knowledge": ["Layers inside an image structure"]
        }
    },
    {
        "domain": "backend",
        "category": "technical",
        "topic": "Docker",
        "difficulty_level": 3,
        "primary_skill": "Volumes",
        "secondary_skills": ["Data Persistence"],
        "question_text": "How do you persist database data when a Docker container stops or is deleted?",
        "expected_concepts": ["Containers are ephemeral", "Docker Volumes", "Bind Mounts"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["Docker containers are stateless/ephemeral", "Use Docker Volumes or Bind Mounts to save data on host OS"],
            "supporting_details": ["Mapping host directory to container directory"],
            "advanced_knowledge": ["Volume drivers for cloud storage"]
        }
    },
    {
        "domain": "backend",
        "category": "technical",
        "topic": "Docker",
        "difficulty_level": 4,
        "primary_skill": "Docker Compose",
        "secondary_skills": ["Multi-container Apps"],
        "question_text": "What is Docker Compose and how does it relate to Docker networking?",
        "expected_concepts": ["YAML file defining multi-container apps", "Automatically creates a bridged network for services to talk to each other"],
        "max_score": 10,
        "scoring_guidelines": {
            "core_concepts": ["Tool for defining and running multi-container applications", "Uses docker-compose.yml"],
            "supporting_details": ["Automatically creates a default network allowing containers to communicate using service names"],
            "advanced_knowledge": ["Not intended for multi-server production orchestrations (unlike Kubernetes)"]
        }
    }
]

def main():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_path = os.path.join(root_dir, "out.json")
    
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=4)
        
    print(f"Successfully generated {len(questions)} perfectly balanced questions to {out_path}.")

if __name__ == "__main__":
    main()
