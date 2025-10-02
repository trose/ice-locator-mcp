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
import { TestFunctionRequest, TestFunctionResult } from "../models/models_1";
export { __MetadataBearer, $Command };
export interface TestFunctionCommandInput extends TestFunctionRequest {}
export interface TestFunctionCommandOutput
  extends TestFunctionResult,
    __MetadataBearer {}
export declare class TestFunctionCommand extends $Command<
  TestFunctionCommandInput,
  TestFunctionCommandOutput,
  CloudFrontClientResolvedConfig
> {
  readonly input: TestFunctionCommandInput;
  static getEndpointParameterInstructions(): EndpointParameterInstructions;
  constructor(input: TestFunctionCommandInput);
  resolveMiddleware(
    clientStack: MiddlewareStack<ServiceInputTypes, ServiceOutputTypes>,
    configuration: CloudFrontClientResolvedConfig,
    options?: __HttpHandlerOptions
  ): Handler<TestFunctionCommandInput, TestFunctionCommandOutput>;
  private serialize;
  private deserialize;
}
