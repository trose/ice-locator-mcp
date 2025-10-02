import { EndpointParameterInstructions } from "@smithy/middleware-endpoint";
import { Command as $Command } from "@smithy/smithy-client";
import {
  Handler,
  HttpHandlerOptions as __HttpHandlerOptions,
  MetadataBearer as __MetadataBearer,
  MiddlewareStack,
} from "@smithy/types";
import {
  CloudFrontClientResolvedConfig,
  ServiceInputTypes,
  ServiceOutputTypes,
} from "../CloudFrontClient";
import {
  DescribeFunctionRequest,
  DescribeFunctionResult,
} from "../models/models_1";
export { __MetadataBearer, $Command };
export interface DescribeFunctionCommandInput extends DescribeFunctionRequest {}
export interface DescribeFunctionCommandOutput
  extends DescribeFunctionResult,
    __MetadataBearer {}
export declare class DescribeFunctionCommand extends $Command<
  DescribeFunctionCommandInput,
  DescribeFunctionCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: DescribeFunctionCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: DescribeFunctionCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<DescribeFunctionCommandInput, DescribeFunctionCommandOutput>;
  private serialize;
  private deserialize;
}
