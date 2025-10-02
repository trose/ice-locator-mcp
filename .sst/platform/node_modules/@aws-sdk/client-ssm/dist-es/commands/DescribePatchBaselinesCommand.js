import { getEndpointPlugin } from "@smithy/middleware-endpoint";
import { getSerdePlugin } from "@smithy/middleware-serde";
import { Command as $Command } from "@smithy/smithy-client";
import { SMITHY_CONTEXT_KEY, } from "@smithy/types";
import { de_DescribePatchBaselinesCommand, se_DescribePatchBaselinesCommand } from "../protocols/Aws_json1_1";
export { $Command };
export class DescribePatchBaselinesCommand extends $Command {
    static getEndpointParameterInstructions() {
        return {
            UseFIPS: { type: "builtInParams", name: "useFipsEndpoint" },
            Endpoint: { type: "builtInParams", name: "endpoint" },
            Region: { type: "builtInParams", name: "region" },
            UseDualStack: { type: "builtInParams", name: "useDualstackEndpoint" },
        };
    }
    constructor(input) {
        super();
        this.input = input;
    }
    resolveMiddleware(clientStack, configuration, options) {
        this.middlewareStack.use(getSerdePlugin(configuration, this.serialize, this.deserialize));
        this.middlewareStack.use(getEndpointPlugin(configuration, DescribePatchBaselinesCommand.getEndpointParameterInstructions()));
        const stack = clientStack.concat(this.middlewareStack);
        const { logger } = configuration;
        const clientName = "SSMClient";
        const commandName = "DescribePatchBaselinesCommand";
        const handlerExecutionContext = {
            logger,
            clientName,
            commandName,
            inputFilterSensitiveLog: (_) => _,
            outputFilterSensitiveLog: (_) => _,
            [SMITHY_CONTEXT_KEY]: {
                service: "AmazonSSM",
                operation: "DescribePatchBaselines",
            },
        };
        const { requestHandler } = configuration;
        return stack.resolve((request) => requestHandler.handle(request.request, options || {}), handlerExecutionContext);
    }
    serialize(input, context) {
        return se_DescribePatchBaselinesCommand(input, context);
    }
    deserialize(output, context) {
        return de_DescribePatchBaselinesCommand(output, context);
    }
}
